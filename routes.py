import os
from flask import render_template, url_for, flash, redirect,request,session, abort, send_from_directory
from flask_login import login_user, current_user, logout_user, login_required
from app import bcrypt, db, create_app
from sqlalchemy.exc import IntegrityError
from models import User,Post, Comment, Like
from werkzeug.utils import secure_filename
import bleach


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_routes(app, db, bcrypt, cache):
    @app.route('/')
    @cache.cached(timeout=60)
    def hello():
        if current_user.is_authenticated:
            user = str(current_user.email)
            return f'{user} is currently logged in.'
        else:
            return 'no user is currently here'
    
    @app.route('/register', methods = ['GET', 'POST'])
    def register():
        """
        The `register` function in this Python code snippet handles user registration by checking
        authentication status, processing form data, hashing passwords, and adding new users to the
        database.
        :return: The `register()` function returns different responses based on the conditions met:
        """
        
        # The line `if current_user.is_authenticated:` is checking if the current user is
        # authenticated or logged in. If the user is authenticated, it means that the user has
        # successfully logged in, and the code inside the `if` block will be executed. Otherwise, if
        # the user is not authenticated, the code inside the `else` block will be executed. This check
        # is commonly used in web applications to control access to certain routes or functionalities
        # based on the user's authentication status.
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm password')

            if not username or not email or not password :
                return "all fields are required",400
            #confirm that passwords match
            if password != confirm_password:
                return "passwords do not match", 400



            from app import bcrypt, db


            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            user = User(username=username,email=email,password=hashed_password)
            try:
                db.session.add(user)
                db.session.commit()
                flash('Account created','success')
                return redirect(url_for('home'))
            except IntegrityError:
                db.session.rollback()
                return "Error: Could not create user. Username or email might already be in use."
        return render_template('register.html')
    
    @app.route("/login", methods=['GET', 'POST'])
    def login():
        """
        The `login` function checks if a user is already authenticated, processes a login form
        submission, and logs the user in if the credentials are valid.
        :return: The `login()` function returns either a redirect to the 'home' route if the user is
        already authenticated or a rendered template for the 'login.html' page if the request method is
        not POST or if the login attempt is unsuccessful.
        """
        
        from models import User
        if current_user.is_authenticated:
            # Redirect if already logged in
            return redirect(url_for('home'))
        
        
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(email=email).first()

            
            
            if user and bcrypt.check_password_hash(user.password, password):
                """adding a session"""
                session["user_id"] = user.id
                login_user(user)  # Log the user in
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Login unsuccessful. Check email and password.', 'danger')
        flash('Please login to continue', 'info')
        return render_template('login.html')

    # Route for user logout
    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for('home'))

    # Home page (requires login)
    @app.route("/home")
    def home():
        return render_template('home.html')

    @app.route('/kijana')
    def kijana():
        if "user" in session:
            user = User.query.get(session["user_id"])
            return f'<h1>{user}</h1>'
        else:
            return render_template('hello.html')
        
#post management
    @app.route('/post/new', methods=['GET', 'POST'])
    @login_required
    def new_post():
        if request.method == 'POST':
            title = request.form['title']
            body = request.form['body']
            if not title or not body:
                flash('Title and content are required.', 'error')
                return redirect(url_for('new_post'))
            
            allowed_tags = ['p', 'strong', 'em', 'blockquote', 'ul', 'ol', 'li', 'a', 'br']
            clean_body = bleach.clean(body, tags=allowed_tags, strip=True)


            new_post = Post(title=title, body=clean_body, user_id=current_user.id)
            db.session.add(new_post)
            db.session.commit()
            flash('Post created successfully', 'success')
            return redirect(url_for('post_detail', post_id=new_post.id))
        return render_template('create_post.html')

#reading posts
    @app.route('/posts')
    def posts():
        page = request.args.get('page', 1, type=int)
        all_posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=1)
        if all_posts:
            return render_template('posts.html', posts=all_posts)
        return render_template('404.html'), 404
# Viewing a single post
    @app.route('/post/<int:post_id>')
    def post_detail(post_id):
        page = request.args.get('page', 1, type=int)
        post = Post.query.get_or_404(post_id)
        return render_template('post_detail.html', post=post)
#editing a post
    @app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_post(post_id):
        post = Post.query.get_or_404(post_id)

        # Check if the current user is the author of the post
        if post.author != current_user:
            abort(403)  # Forbidden

        if request.method == 'POST':
            post.title = request.form['title']
            post.body = request.form['body']
            db.session.commit()
            return redirect(url_for('post_detail', post_id=post.id))
    
        return render_template('edit_post.html', post=post)
    
    #delete a post
    @app.route('/post/<int:post_id>/delete', methods=['POST'])
    @login_required
    def delete_post(post_id):
        post = Post.query.get_or_404(post_id)

        # Check if the current user is the author of the post
        if post.author != current_user:
            abort(403)

        Comment.query.filter_by(post_id=post.id).delete()

        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('posts'))
    
    #adding user profile
    @app.route('/profile')
    @login_required
    def profile():
        user=current_user
        return render_template('profile.html', user=user)

    #edit profile
    @app.route('/profile/edit', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        user= current_user
        if request.method == 'POST':
            if 'profile_photo' in request.files:
                profile_photo = request.files['profile_photo']
                if profile_photo and allowed_file(profile_photo.filename):
                    filename = secure_filename(profile_photo.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                    # Save the profile photo to the specified folder
                    profile_photo.save(filepath)
                
                    # Update the user's profile photo in the database
                    user.profile_photo = filename
                new_username = request.form['username']
                new_email = request.form['email']

        # Update the user's information
            user.username = new_username
            user.email = new_email

            db.session.commit()
            flash('Your profile has been updated.', 'success')
            return redirect(url_for('profile'))

        return render_template('edit_profile.html', user=user)

    #searching
    @app.route('/search')
    def search():
        author = User.username
        query = request.args.get('query')  # Get the search term from the URL parameters
        if not query:
            return redirect(url_for('home'))  # Redirect to homepage if no query was provided
    
        # Search posts that match the query
        search_results = Post.query.filter(Post.title.ilike(f"%{query}%") |Post.body.ilike(f"%{query}%") | User.email.ilike(f"%{query}%")).all()
    
        return render_template('search_results.html', query=query, posts=search_results)

    #about page
    @app.route('/about')
    def about():
        return render_template('about.html')
    

    @app.route('/post/<int:post_id>/comment', methods=['POST'])
    @login_required
    def add_comment(post_id):
        post = Post.query.get_or_404(post_id)
        content = request.form['content']

    # Create and add the new comment
        comment = Comment(content=content, user_id=current_user.id, post_id=post.id)
        db.session.add(comment)
        db.session.commit()     

        flash('Your comment has been added!')
        return redirect(url_for('post_detail', post_id=post.id))

    @app.route('/post/<int:post_id>/like', methods=['POST'])
    @login_required
    def like_post(post_id):
        post = Post.query.get_or_404(post_id)

        # Check if the user has already liked the post
        like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()

        if like:
        # Unlike if the post is already liked
            db.session.delete(like)
            db.session.commit()
            flash('You unliked the post.')
        else:
            # Add a new like
            like = Like(user_id=current_user.id, post_id=post_id)
            db.session.add(like)
            db.session.commit()
            flash('You liked the post.')

        return redirect(url_for('post_detail', post_id=post.id))
    
    #file uploads
    @app.route('/upload_profile_photo', methods=['POST'])
    def upload_profile_photo():
        user = current_user
        if 'profile_photo' not in request.files:
            flash('No file part')
            return redirect(request.url)
    
        file = request.files['profile_photo']
    
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
    
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            user.profile_photo = filename            
            db.session.commit()
            flash('Profile photo uploaded successfully')
            print(current_user.profile_photo)

            return redirect(url_for('profile'))
        else:
            flash('File type not allowed')
            return redirect(request.url)
    
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        user = current_user
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


    #error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404




