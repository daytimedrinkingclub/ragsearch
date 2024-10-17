from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.models.system_model import System
from extensions import db

system_bp = Blueprint('system', __name__, url_prefix='/system')

@system_bp.route('/prompt', methods=['GET'])
def prompt():
    system_prompt = System.query.filter_by(key='system_prompt').first()
    return render_template('system_prompt.html', system_prompt=system_prompt.value if system_prompt else '', active_tab='System Prompt')

@system_bp.route('/update_prompt', methods=['POST'])
def update_prompt():
    new_prompt = request.form['system_prompt']
    system_prompt = System.query.filter_by(key='system_prompt').first()
    if system_prompt:
        system_prompt.value = new_prompt
    else:
        new_system_prompt = System(key='system_prompt', value=new_prompt)
        db.session.add(new_system_prompt)
    db.session.commit()
    current_app.logger.debug(f"Updated system prompt: {new_prompt}")  # Debugging line
    flash('System prompt updated successfully', 'success')
    return redirect(url_for('system.prompt'))

@system_bp.route('/test_prompt', methods=['GET'])
def test_prompt():
    system_prompt = System.query.filter_by(key='system_prompt').first()
    return f"Current system prompt: {system_prompt.value if system_prompt else 'Not set'}"