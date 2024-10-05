from flask import Flask,render_template,flash,redirect,url_for,session,logging,request

from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps

#kullanıcı giriş decoratoru
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
         return f(*args, **kwargs)
        else:
            flash("Giriş Yapmalısınız görüntülemek için")
            return redirect(url_for("login"))
    return decorated_function




#kayıt formu
class RegisterForm(Form):
    name=StringField("İsim Soyisim",validators=[validators.Length(min=4,max=25)])
    email=StringField("Email",validators=[validators.Email(message= "Geçerli mail giriniz")])
    password=PasswordField("Şifrenizi giriniz",validators=[validators.DataRequired(message="lütfen parola belirle"),validators.EqualTo(fieldname= "confirm",message="parola uyuşmuyor")])
    confirm= PasswordField("Doğrula")
class LoginForm(Form):
    email=StringField("Email giriniz",validators=[validators.Email(message="Geçerli mail giriniz")])
    password=PasswordField("Şifrenizi giriniz",validators=[validators.DataRequired(message="Lütfen şifrenizi girin")])
class ArticleForm(Form):
    title=StringField("Başlık Giriniz",validators=[validators.DataRequired(message="Lütfen eksik bilgi bırakmayın")])
    author=StringField("Yazar Giriniz",validators=[validators.DataRequired(message="Lütfen eksik bilgi bırakmayın")])
    




app = Flask(__name__)
app.secret_key="blog"

app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]=""
app.config["MYSQL_DB"]="blog"
app.config["MYSQL_CURSORCLASS"]="DictCursor"

mysql=MySQL(app)


@app.route("/")     #decorator
def index():
    number=10
    name="eray"
    article=dict()
    article["title"]="deneme"
    article["body"]="deneme123"
    return  render_template("index.html",_number=number,_name=name,_article=article)

@app.route("/anasayfa")
def anasayfa():
    sözlüklistesi = [
        {"id":1,"title":"deneme1"},
        {"id":2,"title":"deneme2"}
    ]    
                                    

    
    return render_template("anasayfa.html",answer="evet",_sözlüklistesi=sözlüklistesi)

@app.route("/about")
def about():
   return render_template("about.html")

@app.route("/inheritancetemplate")
def index1():
    return render_template("index1.html")

@app.route("/bootstrapt")
def index2():
    return render_template("index2.html")

@app.route("/makale/<string:id>")
def detay(id):
    return  "id " + id



@app.route("/register",methods=["GET","POST"])                              
def register():                                                             
                                                                            
                                                                               
    form=RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        print("validate başarılı")
        name= form.name.data
        email=form.email.data
        password=sha256_crypt.hash(form.password.data)
        
        try:
            cursor=mysql.connection.cursor()
            print("bağlanti başarili")
            try:
         
             cursor.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)",(name,email,password))
             mysql.connection.commit()
             
             print("kayit başarili")
             flash("Kayıt oldunuz","success")
             return redirect(url_for("login"))
            except Exception as e:
             print(f"veritabani hatasi: {e}")
             return "kayit başarisiz"
        except Exception as e:
            print(f"baglanti hatasi:{e}")
            return "başarısız"

    else:
        return render_template("register.html",form=form)


@app.route("/login",methods=["GET","POST"])
def login():
    form=LoginForm(request.form)
    if request.method=="POST":
        email=form.email.data
        password=form.password.data
        cursor=mysql.connection.cursor()
        result=cursor.execute("SELECT * FROM users WHERE email =%s",(email,))
        if result !=0:
            data=cursor.fetchone()
            real_password=data["password"]
            if sha256_crypt.verify(password,real_password):
                flash("Başarılı Giriş")
                session["logged_in"]=True
                session["email"]=email
                return redirect(url_for("anasayfa"))
            else:
                flash("Hatalı şifre")
                return redirect(url_for("login"))
            
        else:
            flash("HATALI GİRİŞ")
            return redirect(url_for("login"))


    return render_template("login.html",form=form)

@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")

@app.route("/dashboard")
@login_required
def dashboard():
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT * FROM articles WHERE author= %s",(session["email"],))
    data=cursor.fetchall()

    return render_template("dashboard.html",data=data)
    
@app.route("/addarticle",methods=["GET","POST"])
def addarticle():
    form=ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        print("validate başarılı")
        title= form.title.data
        author= form.author.data
        cursor= mysql.connection.cursor()
        print("bağlantı başarılı")
        cursor.execute("INSERT INTO articles(title,author) VALUES (%s,%s)",(title,author))
        mysql.connection.commit()
        flash("Makale ekleme başarılı")
        return redirect(url_for("dashboard"))
    else:
      return render_template("addarticle.html",form=form)



@app.route("/articles")
def articles():
  if session.get("logged_in"):
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT * FROM articles")
    data = (cursor.fetchall())
    return render_template("articles.html",data=data)
  else:
      return redirect(url_for("login"))
  
@app.route("/article/<string:id>")
def article(id):
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT * FROM articles Where id= %s",(id,))
    data=cursor.fetchall()
    return render_template("article.html",data=data)
@app.route("/delete/<string:id>")
def delete(id):
  if session["logged_in"]:
   cursor=mysql.connection.cursor()

   result=cursor.execute("SELECT * FROM articles where author=%s",(session["email"],))
   
   if result!=0:
      cursor.execute("DELETE FROM articles where id=%s",(id,))
      mysql.connection.commit()
      flash("silindi")
      return redirect(url_for("dashboard"))
   else:
      print("Sadece kendi makaleni silebilirsin")
  else:
     print("giriş yapmalısınız")


 
@app.route("/edit/<string:id>",methods=["GET","POST"])
@login_required
def edit(id):
  if request.method=="GET":
   cursor=mysql.connection.cursor()
   cursor.execute("SELECT * FROM articles Where id= %s",(id,))
   data=cursor.fetchone()
   form=ArticleForm()
   form.title.data=data["title"]
   form.author.data=data["author"]
   return render_template("edit.html",form=form)  
  else:
    form=ArticleForm(request.form)
    title=form.title.data
    author=form.author.data

    cursor=mysql.connection.cursor()
    cursor.execute("UPDATE articles SET title=%s,author=%s where id=%s",(title,author,id))
    mysql.connection.commit()
    flash("Güncellendi")
    return redirect(url_for("dashboard"))
  
  
@app.route("/search",methods=["GET","POST"])
def search():
   keyword=request.form.get("keyword")
   cursor=mysql.connection.cursor()
   cursor.execute("SELECT * from articles where title like '%" + keyword +"%'")
   data=cursor.fetchall()
   return render_template("articles.html",data=data)
   
  
   
      
      
      
    







if __name__ =="__main__":
    app.run(debug=True)
