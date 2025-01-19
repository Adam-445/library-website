from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mssql.information_schema import constraints
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, CheckConstraint


app = Flask(__name__)

class Base(DeclarativeBase):
    pass

#Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///book-library.db"
db= SQLAlchemy(model_class=Base)
db.init_app(app)

#Define a model
class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    rating: Mapped[float] = mapped_column(Float, CheckConstraint("rating BETWEEN 0 AND 10"),nullable=False)
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    with app.app_context():
        result = db.session.execute(db.select(Book).order_by(Book.title))
        all_books = list(result.scalars())
    return render_template('index.html', books=all_books)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        try:
            with app.app_context():
                new_book = Book(
                    title=request.form["book-title"],
                    author=request.form["author"],
                    rating=request.form["rating"]
                )
                db.session.add(new_book)
                db.session.commit()
        except IntegrityError as err:
            print(f"Error occurred : {err}")
            return render_template('add.html')
        else:
            return redirect(url_for('home'))

    return render_template('add.html')


@app.route('/edit', methods=["GET", "POST"])
def edit_rating():
    # Find the book attributes
    book_id = request.args.get('id')
    with app.app_context():
        book = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
        if request.method == "POST":
            try:
                book.rating= request.form["new-rating"]
                db.session.commit()
            except IntegrityError as err:
                print("Encountered an error: {err}")
            finally:
                return redirect(url_for('home'))

    return render_template('edit.html', book=book)


@app.route('/delete-book')
def delete_book():
    with app.app_context():
        if request.args.get('id'):
            book_id = request.args.get('id')
            book_to_delete = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
            db.session.delete(book_to_delete)
            db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)

