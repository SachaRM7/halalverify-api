#!/usr/bin/env python3
from __future__ import annotations

import os
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_cors import CORS

from api.routes import api_bp
from models import db
from models.charity import Charity
from models.donation import Donation
from models.goal import GivingGoal
from models.review import Review
from services.community_sync import sync_community_data
from services.pdf_generator import build_receipt_pdf
from services.zakat_calculator import calculate_zakat_due


DEFAULT_CONFIG = {
    'SECRET_KEY': 'dev-secret-key',
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///instance/sadaqah.db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'COMMUNITY_JSON_URL': '',
    'COMMUNITY_SYNC_ON_STARTUP': False,
    'COMMUNITY_SHARED_PASSPHRASE': 'change-me',
    'TELEGRAM_BOT_TOKEN': '',
    'TELEGRAM_CHAT_ID': '',
    'APP_BASE_URL': 'http://127.0.0.1:5000',
    'DEFAULT_NISAB_THRESHOLD': 5500.0,
}

SEED_CHARITIES = [
    {'name': 'Islamic Relief Worldwide', 'website': 'https://www.islamic-relief.org', 'registration_country': 'United Kingdom', 'cause_areas': 'emergency,water,education', 'description': 'Global humanitarian charity serving vulnerable communities.', 'reports_json': ['https://www.islamic-relief.org/publications/annual-reports/']},
    {'name': 'Muslim Hands', 'website': 'https://muslimhands.org.uk', 'registration_country': 'United Kingdom', 'cause_areas': 'food,education,health', 'description': 'Runs education, livelihoods, and emergency response projects.', 'reports_json': ['https://muslimhands.org.uk/our-work/reports']},
    {'name': 'Penny Appeal', 'website': 'https://pennyappeal.org', 'registration_country': 'United Kingdom', 'cause_areas': 'water,orphans,emergency', 'description': 'Well-known for water and orphan support campaigns.', 'reports_json': ['https://pennyappeal.org/about-us/reports']},
    {'name': 'LaunchGood Relief', 'website': 'https://www.launchgood.com', 'registration_country': 'United States', 'cause_areas': 'community,emergency,crowdfunding', 'description': 'Crowdfunding ecosystem with community impact campaigns.', 'reports_json': ['https://www.launchgood.com']},
    {'name': 'MATW Project', 'website': 'https://matwproject.org', 'registration_country': 'Australia', 'cause_areas': 'water,food,orphans', 'description': 'Global Muslim charity focused on direct aid and sustainable impact.', 'reports_json': ['https://matwproject.org/pages/reports']},
    {'name': 'Human Appeal', 'website': 'https://humanappeal.org.uk', 'registration_country': 'United Kingdom', 'cause_areas': 'health,water,emergency', 'description': 'Delivers emergency relief and sustainable development projects.', 'reports_json': ['https://humanappeal.org.uk/about-us/reports']},
    {'name': 'Zakat Foundation of America', 'website': 'https://www.zakat.org', 'registration_country': 'United States', 'cause_areas': 'zakat,education,refugees', 'description': 'Focuses on zakat distribution and community development.', 'reports_json': ['https://www.zakat.org/about-us/annual-reports/']},
    {'name': 'National Zakat Foundation', 'website': 'https://nzf.org.uk', 'registration_country': 'United Kingdom', 'cause_areas': 'zakat,poverty,community', 'description': 'Localized zakat distribution for Muslims in hardship.', 'reports_json': ['https://nzf.org.uk/about-us']},
    {'name': 'Helping Hand for Relief and Development', 'website': 'https://hhrd.org', 'registration_country': 'United States', 'cause_areas': 'food,health,water', 'description': 'Provides emergency and long-term support in multiple countries.', 'reports_json': ['https://hhrd.org/publications/annual-reports/']},
    {'name': 'Direct Aid Society', 'website': 'https://direct-aid.org', 'registration_country': 'Kuwait', 'cause_areas': 'health,education,orphans', 'description': 'Long-running charity active in Africa and Asia.', 'reports_json': ['https://direct-aid.org']},
    {'name': 'Ummah Welfare Trust', 'website': 'https://uwt.org', 'registration_country': 'United Kingdom', 'cause_areas': 'emergency,water,food', 'description': 'Emergency aid and sustainable livelihoods for vulnerable families.', 'reports_json': ['https://uwt.org/reports']},
    {'name': 'Baitulmaal', 'website': 'https://baitulmaal.org', 'registration_country': 'United States', 'cause_areas': 'food,water,refugees', 'description': 'Muslim NGO delivering aid to refugees and low-income households.', 'reports_json': ['https://baitulmaal.org/about-us']},
    {'name': 'Hasene International', 'website': 'https://www.hasene.org', 'registration_country': 'Germany', 'cause_areas': 'food,education,water', 'description': 'Provides humanitarian assistance and development projects.', 'reports_json': ['https://www.hasene.org/en']},
    {'name': 'Read Foundation', 'website': 'https://readfoundation.org.uk', 'registration_country': 'United Kingdom', 'cause_areas': 'education,children,community', 'description': 'Builds and supports schools in underserved communities.', 'reports_json': ['https://readfoundation.org.uk/about-us/']},
    {'name': 'SKT Welfare', 'website': 'https://www.sktwelfare.org', 'registration_country': 'United Kingdom', 'cause_areas': 'water,health,food', 'description': 'Delivers food, water, and healthcare interventions.', 'reports_json': ['https://www.sktwelfare.org/annual-report']},
    {'name': 'Al-Khair Foundation', 'website': 'https://alkhair.org', 'registration_country': 'United Kingdom', 'cause_areas': 'water,education,emergency', 'description': 'Implements global water, orphan, and emergency campaigns.', 'reports_json': ['https://alkhair.org/about-us/']},
    {'name': 'One Nation UK', 'website': 'https://onenationuk.org', 'registration_country': 'United Kingdom', 'cause_areas': 'emergency,food,shelter', 'description': 'Delivers emergency response in crisis zones.', 'reports_json': ['https://onenationuk.org']},
    {'name': 'Mercy Without Limits', 'website': 'https://mwlimits.org', 'registration_country': 'United States', 'cause_areas': 'orphans,education,water', 'description': 'Supports orphan care and sustainable education.', 'reports_json': ['https://mwlimits.org/about-us/']},
    {'name': 'Islamic Relief Canada', 'website': 'https://islamicreliefcanada.org', 'registration_country': 'Canada', 'cause_areas': 'food,water,community', 'description': 'Canadian branch with domestic and international aid programs.', 'reports_json': ['https://www.islamicreliefcanada.org/about-us/annual-reports/']},
    {'name': 'Rahma Worldwide', 'website': 'https://rahmaww.org', 'registration_country': 'United States', 'cause_areas': 'health,food,refugees', 'description': 'Aid and medical support for refugees and crisis-affected people.', 'reports_json': ['https://rahmaww.org/about/']},
]


def _load_yaml_config(instance_path: str) -> dict[str, Any]:
    for candidate in (Path.cwd() / 'config.yaml', Path(instance_path) / 'config.yaml'):
        if candidate.exists():
            with candidate.open('r', encoding='utf-8') as handle:
                return yaml.safe_load(handle) or {}
    return {}


def seed_charities() -> None:
    if Charity.query.count() >= 20:
        return
    existing = {c.name for c in Charity.query.all()}
    for item in SEED_CHARITIES:
        if item['name'] in existing:
            continue
        db.session.add(Charity.from_seed(item))
    db.session.commit()


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(DEFAULT_CONFIG)
    os.makedirs(app.instance_path, exist_ok=True)
    app.config.update(_load_yaml_config(app.instance_path))
    if test_config:
        app.config.update(test_config)

    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri.startswith('sqlite:///') and not db_uri.startswith('sqlite:////'):
        relative_path = db_uri.replace('sqlite:///', '', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{(Path(app.root_path) / relative_path).resolve()}"

    db.init_app(app)
    CORS(app, resources={r'/api/*': {'origins': '*'}})
    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()
        seed_charities()
        if app.config.get('COMMUNITY_SYNC_ON_STARTUP'):
            sync_community_data(app.config.get('COMMUNITY_JSON_URL', ''))

    @app.context_processor
    def inject_globals() -> dict[str, Any]:
        goal = GivingGoal.get_primary()
        return {'active_goal': goal}

    @app.route('/')
    def index() -> str:
        donations = Donation.query.order_by(Donation.date.asc()).all()
        today = date.today()
        total_all = sum(d.amount for d in donations)
        total_year = sum(d.amount for d in donations if d.date.year == today.year)
        total_month = sum(d.amount for d in donations if d.date.year == today.year and d.date.month == today.month)
        by_type = defaultdict(float)
        by_category = defaultdict(float)
        monthly = defaultdict(float)
        for donation in donations:
            by_type[donation.donation_type] += donation.amount
            by_category[donation.category] += donation.amount
            monthly[donation.date.strftime('%Y-%m')] += donation.amount
        goal = GivingGoal.get_primary()
        goal_progress = 0.0
        suggested_due = 0.0
        if goal:
            suggested_due = calculate_zakat_due(goal.assets, goal.liabilities, goal.nisab_threshold)
            if goal.annual_zakat_goal:
                goal_progress = round((total_year / goal.annual_zakat_goal) * 100, 1) if goal.annual_zakat_goal else 0.0
        top_charities = Charity.top_rated(limit=5, preferred_causes=goal.preferred_causes if goal else '')
        chart_labels = list(monthly.keys())
        chart_values = [round(v, 2) for v in monthly.values()]
        return render_template(
            'index.html',
            total_all=round(total_all, 2),
            total_year=round(total_year, 2),
            total_month=round(total_month, 2),
            by_type=dict(by_type),
            by_category=dict(by_category),
            chart_labels=chart_labels,
            chart_values=chart_values,
            goal=goal,
            goal_progress=goal_progress,
            suggested_due=suggested_due,
            top_charities=top_charities,
            donation_count=len(donations),
        )

    @app.route('/donations', methods=['GET', 'POST'])
    def donations() -> str:
        if request.method == 'POST':
            charity_id = request.form.get('charity_id') or None
            charity = db.session.get(Charity, int(charity_id)) if charity_id else None
            donation = Donation(
                donation_type=request.form['donation_type'],
                amount=float(request.form['amount']),
                currency=request.form.get('currency', 'USD'),
                charity_name=charity.name if charity else request.form.get('charity_name', '').strip(),
                charity_id=charity.id if charity else None,
                date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                category=request.form['category'],
                note=request.form.get('note', '').strip(),
            )
            db.session.add(donation)
            db.session.commit()
            flash('Donation logged successfully.', 'success')
            return redirect(url_for('donations'))
        all_donations = Donation.query.order_by(Donation.date.desc()).all()
        charities = Charity.query.order_by(Charity.name.asc()).all()
        return render_template('donations.html', donations=all_donations, charities=charities, today=date.today().isoformat())

    @app.route('/charities', methods=['GET', 'POST'])
    def charities() -> str:
        if request.method == 'POST':
            charity = Charity(
                name=request.form['name'],
                website=request.form.get('website', ''),
                registration_country=request.form.get('registration_country', ''),
                cause_areas=request.form.get('cause_areas', ''),
                description=request.form.get('description', ''),
            )
            db.session.add(charity)
            db.session.commit()
            flash('Charity submitted locally.', 'success')
            return redirect(url_for('charities'))
        query = request.args.get('q', '').strip().lower()
        items = Charity.query.order_by(Charity.name.asc()).all()
        if query:
            items = [c for c in items if query in c.search_blob]
        return render_template('charities.html', charities=items, query=query)

    @app.route('/charities/<int:charity_id>', methods=['GET', 'POST'])
    def charity_detail(charity_id: int) -> str:
        charity = db.get_or_404(Charity, charity_id)
        if request.method == 'POST':
            review = Review(
                charity_id=charity.id,
                reviewer_name=request.form.get('reviewer_name', '').strip() or 'Anonymous',
                rating=int(request.form['rating']),
                review_text=request.form.get('review_text', '').strip(),
                is_local_only=True,
            )
            db.session.add(review)
            db.session.commit()
            flash('Review saved locally.', 'success')
            return redirect(url_for('charity_detail', charity_id=charity.id))
        donations = Donation.query.filter_by(charity_id=charity.id).order_by(Donation.date.desc()).all()
        return render_template('charity_detail.html', charity=charity, donations=donations)

    @app.route('/goals', methods=['GET', 'POST'])
    def goals() -> str:
        goal = GivingGoal.get_primary() or GivingGoal()
        if request.method == 'POST':
            goal.annual_zakat_goal = float(request.form.get('annual_zakat_goal') or 0)
            goal.monthly_sadaqah_target = float(request.form.get('monthly_sadaqah_target') or 0)
            goal.assets = float(request.form.get('assets') or 0)
            goal.liabilities = float(request.form.get('liabilities') or 0)
            goal.nisab_threshold = float(request.form.get('nisab_threshold') or app.config['DEFAULT_NISAB_THRESHOLD'])
            goal.donor_name = request.form.get('donor_name', '')
            goal.telegram_chat_id = request.form.get('telegram_chat_id', '')
            goal.preferred_causes = request.form.get('preferred_causes', '')
            db.session.add(goal)
            db.session.commit()
            flash('Goals updated.', 'success')
            return redirect(url_for('goals'))
        suggested_due = calculate_zakat_due(goal.assets, goal.liabilities, goal.nisab_threshold)
        return render_template('goals.html', goal=goal, suggested_due=suggested_due)

    @app.route('/reports', methods=['GET', 'POST'])
    def reports() -> str:
        donations = Donation.query.order_by(Donation.date.desc()).all()
        if request.method == 'POST':
            selected_ids = [int(item) for item in request.form.getlist('donation_ids')]
            selected = Donation.query.filter(Donation.id.in_(selected_ids)).order_by(Donation.date.asc()).all()
            donor_name = request.form.get('donor_name') or (GivingGoal.get_primary().donor_name if GivingGoal.get_primary() else '')
            output_path = Path(app.instance_path) / 'receipt.pdf'
            build_receipt_pdf(selected, output_path, donor_name=donor_name, base_url=app.config.get('APP_BASE_URL', 'http://127.0.0.1:5000'))
            return send_file(output_path, as_attachment=True, download_name='sadaqah_receipt.pdf')
        return render_template('reports.html', donations=donations)

    @app.route('/api-docs')
    def api_docs() -> str:
        return render_template('api_docs.html')

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
