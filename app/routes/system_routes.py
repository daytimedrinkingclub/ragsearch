from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.models.system_model import System
from extensions import db

system_bp = Blueprint('system', __name__, url_prefix='/system')

@system_bp.route('/prompt', methods=['GET'])
def prompt():
    system_prompts = System.query.all()
    return render_template('system_prompt.html', system_prompts=system_prompts, active_tab='System Prompt')

@system_bp.route('/add_prompt', methods=['GET'])
def add_prompt():
    new_prompt = System(key="", value="")
    return render_template('edit_system_prompt.html', system_prompt=new_prompt, active_tab='System Prompt')

@system_bp.route('/edit_prompt/<prompt_key>', methods=['GET'])
def edit_prompt(prompt_key):
    system_prompt = System.query.filter_by(key=prompt_key).first()
    return render_template('edit_system_prompt.html', system_prompt=system_prompt, active_tab='System Prompt')

@system_bp.route('/update_prompt', methods=['POST'])
def update_prompt():
    prompt_key = request.form['system_prompt_key']
    prompt_value = request.form['system_prompt_value']
    system_prompt = System.query.filter_by(key=prompt_key).first()
    if system_prompt:
        system_prompt.value = prompt_value
    else:
        new_system_prompt = System(key=prompt_key, value=prompt_value)
        db.session.add(new_system_prompt)
    db.session.commit()
    current_app.logger.debug(f"Updated system prompt: {prompt_key}: {prompt_value}")  # Debugging line
    flash('System prompt updated successfully', 'success')
    return redirect(url_for('system.prompt'))


@system_bp.route('/delete_prompt', methods=['POST'])
def delete_prompt():
    data = request.form
    prompt_key = data.get('prompt_key')
    if not prompt_key:
        return jsonify({"error": "Missing prompt_key in request body"}), 400

    try:
        system_prompt = System.query.filter_by(key=prompt_key).first()
        if system_prompt:
            db.session.delete(system_prompt)
            db.session.commit()
        return redirect(url_for('system.prompt'))
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500