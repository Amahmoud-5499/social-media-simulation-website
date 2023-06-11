from itertools import chain
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User,auth
from django.contrib import messages
from core.models import Profile, Post, LikePost, FollowersCount
from django.db import transaction
from django.contrib.auth.decorators import login_required
import random

# Create your views here.

# view for home page
@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)
    for users in user_following:
        user_following_list.append(users.user)
    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))
    print(feed_list)
    # posts = Post.objects.all()

    # user suggestion
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)
    
    new_suggestion_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestion_list = [x for x in list(new_suggestion_list) if (x not in list(current_user))]
    random.shuffle(final_suggestion_list)
    
    username_profile = []
    username_profile_list = []
    for users in final_suggestion_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)
    suggestion_username_profile_list = list(chain(*username_profile_list))
    print(username_profile_list)


    return render(request, 'index.html',{
        'user_profile':user_profile,
        'posts':feed_list,
        'suggestion_username_profile_list':suggestion_username_profile_list[:3],
        })


# view for settings page
@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        if request.FILES.get('image') == None:
        
            image = user_profile.profile_img
        else:
            image = request.FILES['image']
        bio = request.POST['bio']
        location = request.POST['location']

        user_profile.profile_img = image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()
        # if request.FILES.get('image') != None:
        #     image = request.FILES['image']
        #     bio = request.POST['bio']
        #     location = request.POST['location']

        #     user_profile.profile_img = image
        #     user_profile.bio = bio
        #     user_profile.location = location
        #     user_profile.save()
        return redirect('settings')

    return render(request, 'setting.html', {'user_profile': user_profile})


# view to register new user
@transaction.atomic # make transaction atomic to rollback if any error
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email,password=password)
                user.save()
                # Log user in and redirect to setting page   
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request,user_login)

                # create a profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request,'Password Not Matching')
            return redirect('signup')
    else:
        return render(request, 'signup.html')


# view to signin page
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')
    else:
        return render(request, 'signin.html')


# view to logout
# @login_required(login_url='signin')
# def logout(request):
#     auth.logout(request)
#     return redirect('signin')


# view to upload a post
@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST.get('caption')

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        return redirect('/')
    else:
        return redirect('/')


# view to show number of likes for post
@login_required(login_url='signin')
def post_like(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()
    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        # post.save()
        # return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
    post.save()
    return redirect('/')


# view to show a profile of user
@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    no_of_posts = len(user_posts)

    follower = request.user.username
    user = pk
    if FollowersCount.objects.filter(user=user, follower=follower).first():
        button_text = "Unfollow"
    else:
        button_text = "Follow"
    number_of_user_followers = len(FollowersCount.objects.filter(user=pk))
    number_of_user_following = len(FollowersCount.objects.filter(follower=pk))
        

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'no_of_posts': no_of_posts,
        'button_text': button_text,
        'number_of_user_followers': number_of_user_followers,
        'number_of_user_following': number_of_user_following,
    }
    return render(request, 'profile.html', context)


# view for followers
@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST.get('follower')
        user = request.POST.get('user')
        if FollowersCount.objects.filter(user=user, follower=follower).first():
            delete_follower = FollowersCount.objects.get(user=user, follower=follower)
            delete_follower.delete()
            # return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(user=user, follower=follower)
            new_follower.save()
        
        return redirect('/profile/'+user)
    else:
        return redirect('/')


# view for searching a username
@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST.get('username').strip()
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)
        username_profile_list = list(chain(*username_profile_list))
        print(username_profile_list)

    return render(request, 'search.html', {'user_profile':user_profile, 'username_profile_list':username_profile_list})