#!/usr/bin/env python3
"""
Webアプリケーション - Flask

タスクID: {task_id}
説明: {description}
生成日時: {timestamp}
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

# アプリケーション初期化
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 拡張機能初期化
db = SQLAlchemy(app)
CORS(app)

# ========================================
# モデル定義
# ========================================

class Item(db.Model):
    """アイテムモデル"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {{
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }}


# ========================================
# ルート（Web UI）
# ========================================

@app.route('/')
def index():
    """トップページ"""
    items = Item.query.order_by(Item.created_at.desc()).all()
    return render_template('index.html', items=items)


@app.route('/items/new', methods=['GET', 'POST'])
def new_item():
    """アイテム作成"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        if not title:
            flash('タイトルは必須です', 'error')
            return redirect(url_for('new_item'))
        
        item = Item(title=title, description=description)
        db.session.add(item)
        db.session.commit()
        
        flash('アイテムを作成しました', 'success')
        return redirect(url_for('index'))
    
    return render_template('new_item.html')


@app.route('/items/<int:item_id>')
def show_item(item_id):
    """アイテム詳細"""
    item = Item.query.get_or_404(item_id)
    return render_template('show_item.html', item=item)


# ========================================
# API エンドポイント
# ========================================

@app.route('/api/items', methods=['GET'])
def api_list_items():
    """アイテム一覧API"""
    items = Item.query.all()
    return jsonify([item.to_dict() for item in items])


@app.route('/api/items', methods=['POST'])
def api_create_item():
    """アイテム作成API"""
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({{'error': 'title is required'}}), 400
    
    item = Item(
        title=data['title'],
        description=data.get('description', '')
    )
    
    db.session.add(item)
    db.session.commit()
    
    return jsonify(item.to_dict()), 201


@app.route('/api/items/<int:item_id>', methods=['GET'])
def api_get_item(item_id):
    """アイテム詳細API"""
    item = Item.query.get_or_404(item_id)
    return jsonify(item.to_dict())


@app.route('/api/items/<int:item_id>', methods=['PUT'])
def api_update_item(item_id):
    """アイテム更新API"""
    item = Item.query.get_or_404(item_id)
    data = request.get_json()
    
    if 'title' in data:
        item.title = data['title']
    if 'description' in data:
        item.description = data['description']
    
    db.session.commit()
    
    return jsonify(item.to_dict())


@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def api_delete_item(item_id):
    """アイテム削除API"""
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    
    return '', 204


# ========================================
# エラーハンドラー
# ========================================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


# ========================================
# 初期化
# ========================================

@app.cli.command()
def init_db():
    """データベース初期化"""
    db.create_all()
    print('Database initialized')


# ========================================
# 起動
# ========================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
