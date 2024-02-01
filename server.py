from flask import Flask, render_template, redirect, flash, request, session
import jinja2
from melons import get_all, look_up
from forms import LoginForm
import customers

app = Flask(__name__)
app.secret_key = 'dev'
app.jinja_env.undefined = jinja2.StrictUndefined

@app.route("/")
def home():
    return render_template("base.html")

@app.route("/melons")
def all_melons():
    melon_list = get_all()
    return render_template("all_melons.html", melon_list=melon_list)

@app.route("/melon/<melon_id>")
def single_melon(melon_id):
    melon = look_up(melon_id)
    return render_template("single_melon.html", melon=melon)

@app.route("/add_to_cart<melon_id>")
def add_to_cart(melon_id):
    if 'username' not in session:
        return redirect("/login")

    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']

    cart[melon_id] = cart.get(melon_id, 0) + 1
    session.modified = True
    flash(f"Melon {melon_id} successfully added to cart.")
    print(cart)
    return redirect("/cart")

@app.route("/cart")
def cart():
    if 'username' not in session:
        return redirect("/login")

    order_total = 0
    cart_melons = []
    cart = session.get("cart", {})

    for melon_id, qty in cart.items():
        melon = look_up(melon_id)

        cost = qty * melon.price
        order_total += cost

        melon.qty = qty
        melon.cost = cost

        cart_melons.append(melon)

    return render_template("cart.html", cart_melons=cart_melons, order_total=order_total)

@app.route("/empty-cart")
def empty_cart():
    session["cart"] = {}

    return redirect("/cart")

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = customers.get_by_username(username)

        if not user or user['password'] != password:
            flash("Invalid username or password")
            return redirect('/login')

        session['username'] = user['username']
        flash('Logged in')
        return redirect('/melons')

    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    del session['username']
    flash('Logged Out Successfully!')
    return redirect('/login')

@app.errorhandler(404)
def error_404(e):
   return render_template("404.html")

if __name__ == "__main__":
    app.run(debug=True, port=8000, host="localhost")
