from flask import render_template, flash
from app import app

@app.route('/')
@app.route('/')
def index():
	return render_template("index.html")