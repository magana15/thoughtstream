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
    @app.route("/home")
    def home():
        return render_template('home.html')
    
    
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
            profile_photo = None

            if 'profile_photo' in request.files:
                photo = request.files['profile_photo']
                if photo and allowed_file(photo.filename):
                    filename = secure_filename(photo.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                    # Save the profile photo to the specified folder
                    photo.save(filepath)
                    
                    user.profile_photo = filename
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            if not username or not email or not password:
                return "all fields are required",400
            #confirm that passwords match
            if password != confirm_password:
                return "passwords do not match", 400



            from app import bcrypt, db


            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            user = User(username=username,email=email,password=hashed_password,profile_photo=profile_photo)
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
        """
        The `new_post` function in Python handles the creation of a new blog post, including image
        upload, form validation, and database insertion.
        :return: The `new_post` function returns either a redirect to the 'new_post' route if there are
        missing required fields (title, image, content), or a redirect to the 'post_detail' route with
        the newly created post's ID if the post is successfully created and saved in the database. If
        the request method is not 'POST', it returns the 'create_post.html' template for rendering the
        """
        if request.method == 'POST':
            if 'blog_image' in request.files:
                blog_image = request.files['blog_image']
                if blog_image and allowed_file(blog_image.filename):
                    filename = secure_filename(blog_image.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                    # Save the profile photo to the uploads folder
                    blog_image.save(filepath)
                
                    # Update the user's profile photo in the database
                    blog_image = filename
            title = request.form['title']
            body = request.form['body']
            
            if not title or not body or not blog_image:
                flash('Title, Image and content are required.', 'error')
                return redirect(url_for('new_post'))
            
            allowed_tags = ['p', 'strong', 'em', 'blockquote', 'ul', 'ol', 'li', 'a', 'br']
            clean_body = bleach.clean(body, tags=allowed_tags, strip=True)


            new_post = Post(title=title, body=clean_body,blog_image=blog_image, user_id=current_user.id)
            db.session.add(new_post)
            db.session.commit()
            flash('Post created successfully', 'success')
            return redirect(url_for('post_detail', post_id=new_post.id))
        return render_template('create_post.html')

#reading posts
    @app.route('/posts')
    def posts():
        """
        This Python function retrieves and paginates posts from a database and renders them on a
        webpage.
        :return: The `posts()` function returns either a rendered template 'posts.html' with the posts
        fetched from the database and paginated, or it returns a rendered template '404.html' with a 404
        status code if there are no posts found.
        """
        
        page = request.args.get('page', 1, type=int)
        all_posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)

        if all_posts:
            return render_template('posts.html', posts=all_posts)
        return render_template('404.html'), 404
# Viewing a single post
    @app.route('/post/<int:post_id>')
    def post_detail(post_id):
        """
        This Python function retrieves details of a specific post and renders them in a template for
        display.
        
        :param post_id: The `post_id` parameter in the `post_detail` function is used to identify the
        specific post for which the details are being requested. It is typically an identifier (such as
        a unique numerical ID) that is used to retrieve the corresponding post from a database or data
        source
        :return: The `post_detail` function is returning the rendered template 'post_detail.html' with
        the `post` variable passed to it. The `post` variable contains the Post object retrieved from
        the database with the given `post_id`.
        """
        page = request.args.get('page', 1, type=int)
        post = Post.query.get_or_404(post_id)
        return render_template('post_detail.html', post=post)
#editing a post
    @app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_post(post_id):
        """
        The function `edit_post` allows a user to edit a post if they are the author of the post.
        
        :param post_id: The `post_id` parameter is the unique identifier of the post that you want to
        edit. It is used to retrieve the specific post from the database so that it can be edited
        :return: The `edit_post` function returns either a redirect to the `post_detail` page for the
        edited post if the request method is POST and the post is successfully updated in the database,
        or it returns the rendered template 'edit_post.html' with the post data if the request method is
        not POST.
        """
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
        """
        The function `delete_post` deletes a post and its associated comments if the current user is the
        author of the post.
        
        :param post_id: The `post_id` parameter is the unique identifier of the post that you want to
        delete from the database. It is used to locate the specific post record in the database and
        perform the deletion operation
        :return: The `delete_post` function is returning a redirect response to the 'posts' route using
        `redirect(url_for('posts'))`. This means that after deleting the post and its associated
        comments from the database, the user will be redirected to the 'posts' page.
        """
        post = Post.query.get_or_404(post_id)

        # Check if the current user is the author of the post
        if post.author != current_user:
            abort(403)

        Comment.query.filter_by(post_id=post.id).delete()

        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('posts'))
    
    #adding user profile
    

    @app.route('/profile/<int:user_id>')
    
    @login_required
    def profile(user_id):
        """
        The function `profile` retrieves a user's information from the database and renders a template
        to display the user's profile.
        
        :param user_id: The `user_id` parameter is the unique identifier of a user in the system. It is
        used to retrieve the user's information from the database using the
        `User.query.get_or_404(user_id)` method. This method queries the database for a user with the
        specified `user_id` and returns
        :return: The `profile` function is returning the rendered template 'profile.html' with the user
        data passed to it as a context variable.
        """
        user= User.query.get_or_404(user_id)
        return render_template('profile.html', user=user)

    #edit profile
    @app.route('/profile/edit', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        """
        The `edit_profile` function handles updating a user's profile information, including their
        profile photo, username, and email.
        """
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
            
            return render_template('profile.html', user=user)

        return render_template('edit_profile.html', user=user)

    #searching
    @app.route('/search')
    def search():
        """
        The `search` function retrieves search query from URL parameters, searches for matching posts in
        the database, and displays the results on a template.
        :return: The `search()` function returns the search results based on the query provided in the
        URL parameters. It searches for posts that match the query in the title or body of the post, as
        well as in the email of the user who created the post. If no query is provided, it redirects to
        the homepage. Finally, it renders a template `search_results.html` with the query and the search
        results
        """
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
        """
        This function retrieves a post with ID 1 from the database and renders the 'about.html'
        template.
        :return: The `about()` function is returning the rendered template 'about.html'.
        """
        post = Post.query.get(1)
        return render_template('about.html')
    

    @app.route('/post/<int:post_id>/comment', methods=['POST'])
    @login_required
    def add_comment(post_id):
        """
        The function `add_comment` adds a new comment to a post in a web application.
        
        :param post_id: The `post_id` parameter is the unique identifier of the post to which the
        comment will be added. It is used to retrieve the specific post from the database to which the
        comment will be associated
        :return: a redirect response to the 'post_detail' route with the post_id parameter set to the id
        of the post that the comment was added to.
        """
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
        """
        This Python function allows a user to like or unlike a post on a social media platform.
        
        :param post_id: The `post_id` parameter in the `like_post` function is used to identify the post
        that the user wants to like or unlike. It is the unique identifier of the post in the database.
        The function retrieves the post with the given `post_id` from the database and then checks if
        the
        :return: The `like_post` function returns a redirect response to the `post_detail` route with
        the `post_id` parameter set to `post.id`.
        """
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
        """
        The function `uploaded_file` retrieves a file from the specified directory and sends it to the
        user.
        
        :param filename: The `filename` parameter is a string that represents the name of the file that
        has been uploaded by the user
        :return: the file specified by the `filename` parameter from the directory specified by
        `app.config['UPLOAD_FOLDER']`.
        """
        user = current_user
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route('/favorite/<int:post_id>', methods=['POST'])
    @login_required
    def favorite_post(post_id):
        """
        The function `favorite_post` adds a post to the current user's favorites if it is not already
        there and displays a message accordingly.
        
        :param post_id: The `post_id` parameter in the `favorite_post` function is used to identify the
        specific post that the user wants to add to their favorites. This function retrieves the post
        with the given `post_id` from the database using `Post.query.get_or_404(post_id)`. If the post
        :return: The `favorite_post` function is returning a redirect response to the 'posts' route
        using `url_for('posts')`.
        """
        post = Post.query.get_or_404(post_id)
        if post not in current_user.favorites:
            current_user.favorites.append(post)
            db.session.commit()
            flash('Post added to favorites!')
        else:
            flash('Post is already in your favorites.')
        return redirect(url_for('posts'))

    @app.route('/unfavorite/<int:post_id>', methods=['POST'])
    @login_required
    def unfavorite_post(post_id):   
        """
        The function `unfavorite_post` removes a post from the current user's favorites list if it
        exists, and provides feedback messages accordingly.
        
        :param post_id: The `post_id` parameter is the unique identifier of the post that the user wants
        to unfavorite. It is used to retrieve the specific post from the database and remove it from the
        user's list of favorite posts
        :return: The `unfavorite_post` function is returning a redirect response to the 'posts' route
        using `url_for('posts')`.
        """
        post = Post.query.get_or_404(post_id)
        if post in current_user.favorites:
            current_user.favorites.remove(post)
            db.session.commit()
            flash('Post removed from favorites.')
        else:
            flash('Post is not in your favorites.')
        return redirect(url_for('posts'))


    @app.route('/favorites')
    @login_required
    def favorites():
        """
        The `favorites` function retrieves the current user's favorite posts and renders them in the
        'favorites.html' template.
        :return: The function `favorites()` is returning a rendered template called 'favorites.html'
        with the user's favorite posts passed as a variable named 'posts'.
        """
        favorite_posts = current_user.favorites  # Retrieve user's favorite posts
        return render_template('favorites.html', posts=favorite_posts)
    #error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404




