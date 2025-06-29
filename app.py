from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key in production

# In-memory storage for demo purposes
users = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_restrictions', methods=['GET', 'POST'])
def set_restrictions():
    if request.method == 'POST':
        restrictions = request.form.getlist('restrictions')
        session['restrictions'] = restrictions
        return redirect(url_for('index'))
    return render_template('set_restrictions.html')

@app.route('/check_ean', methods=['GET', 'POST'])
def check_ean():
    result = None
    product_name = None
    if request.method == 'POST':
        ean = request.form['ean']
        restrictions = session.get('restrictions', [])
        # Query go-upc.com API
        api_url = f'https://go-upc.com/api/v1/code/{ean}'
        try:
            resp = requests.get(api_url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                product = data.get('product', {})
                product_name = product.get('name', 'Unknown product')
                # Try to get ingredients from the API response
                ingredients = product.get('ingredients', '')
                if ingredients:
                    # Split ingredients by comma, lowercased and stripped
                    ingredients_list = [i.strip().lower() for i in ingredients.split(',')]
                    if any(r.lower() in ingredients_list for r in restrictions):
                        result = f"{product_name} is NOT suitable for you."
                    else:
                        result = f"{product_name} is OK for you."
                else:
                    result = f"{product_name}: No ingredient info available."
            else:
                result = 'Product not found.'
        except Exception as e:
            result = f'Error contacting product API: {e}'
    return render_template('check_ean.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
