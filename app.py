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
        # Try go-upc.com API first
        api_url_go_upc = f'https://go-upc.com/api/v1/code/{ean}'
        # Open Food Facts API
        api_url_off = f'https://world.openfoodfacts.org/api/v0/product/{ean}.json'
        # Open Product Data (POD) API
        api_url_pod = f'https://pod.opendatasoft.com/api/records/1.0/search/?dataset=open-products&q={ean}'
        # OpenUPC API (free tier, limited)
        api_url_openupc = f'https://api.upcdatabase.org/product/{ean}'
        try:
            # 1. Try go-upc.com
            resp = requests.get(api_url_go_upc, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                product = data.get('product', {})
                product_name = product.get('name', 'Unknown product')
                ingredients = product.get('ingredients', '')
                if ingredients:
                    ingredients_list = [i.strip().lower() for i in ingredients.split(',')]
                    if any(r.lower() in ingredients_list for r in restrictions):
                        result = f"{product_name} is NOT suitable for you."
                    else:
                        result = f"{product_name} is OK for you."
                else:
                    result = f"{product_name}: No ingredient info available."
                return render_template('check_ean.html', result=result)
            else:
                print(f"go-upc.com API error: status={resp.status_code}, response={resp.text}")
            # 2. Try Open Food Facts
            # resp = requests.get(api_url_off, timeout=5)
            # if resp.status_code == 200:
            #     data = resp.json()
            #     product = data.get('product', {})
            #     product_name = product.get('product_name', 'Unknown product')
            #     ingredients = product.get('ingredients_text_en') or product.get('ingredients_text') or ''
            #     if ingredients:
            #         ingredients_list = [i.strip().lower() for i in ingredients.split(',')]
            #         if any(r.lower() in ingredients_list for r in restrictions):
            #             result = f"{product_name} is NOT suitable for you."
            #         else:
            #             result = f"{product_name} is OK for you."
            #     else:
            #         result = f"{product_name}: No ingredient info available."
            #     return render_template('check_ean.html', result=result)
            # else:
            #     print(f"Open Food Facts API error: status={resp.status_code}, response={resp.text}")
            # 3. Try Open Product Data (POD)
            resp = requests.get(api_url_pod, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                records = data.get('records', [])
                if records:
                    product = records[0]['fields']
                    product_name = product.get('product_name', product.get('name', 'Unknown product'))
                    # POD may not have ingredients, so just show product name
                    result = f"{product_name}: No ingredient info available."
                else:
                    result = 'Product not found in Open Product Data.'
                return render_template('check_ean.html', result=result)
            else:
                print(f"Open Product Data API error: status={resp.status_code}, response={resp.text}")
            # 4. Try OpenUPC
            resp = requests.get(api_url_openupc, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                product_name = data.get('title', 'Unknown product')
                # OpenUPC does not provide ingredients in free tier
                result = f"{product_name}: No ingredient info available."
                return render_template('check_ean.html', result=result)
            else:
                print(f"OpenUPC API error: status={resp.status_code}, response={resp.text}")
                result = 'Product not found.'
        except Exception as e:
            result = f'Error contacting product APIs: {e}'
    return render_template('check_ean.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
