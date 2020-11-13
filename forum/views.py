from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages  # for flash messages
from .models import *
# from .forms import CreateUserForm
from .forms import *


# for restricting users without login
from django.contrib.auth.decorators import login_required

# Create your views here.


def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user_msg = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for '+user_msg)

                # redirecting user after successful login
                # you can also place landingPage here
                return redirect('login')

        context = {'form': form}
        return render(request, 'forum/register.html', context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
        # return redirect('forum/1')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            # request.POST.get('yearOfAdmission')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                # landingpage should come here DOUBTFULL, earlier it was home
                return redirect('home')
                # return redirect('forum/1')
            else:
                messages.info(request, 'Username OR Password is incorrect')

        context = {}
        return render(request, 'forum/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('landingPage')


def landingPage(request):
    return render(request, 'forum/landingPage.html', {})

# @login_required(login_url='landing')
# put the below line above every view that you want to restrict if the user hasn't loggedin
# these are nothing but login decorators


@login_required(login_url='login')
def home(request):
    # context = {}
    # return render(request, 'forum/main.html', {})
    return redirect("forum", page=1)


@login_required(login_url='login')
def forum(request, page):
    questions = Question.objects.all().order_by('-created_on')
    min_index = (page-1)*10
    max_index = min((page*10)-1, len(questions)-1)
    if len(questions) % 10 == 0:
        max_page = len(questions)//10
    else:
        max_page = len(questions)//10 + 1
    context = {'questions': questions[min_index:max_index+1],
               'next_page': min(page+1, max_page),
               'previous_page': max(page-1, 1)
               }
    return render(request, 'forum/forum.html', context)

#
# answer crud
#


@login_required(login_url='login')
def question_create(request):
    form = QuestionCreateForm(initial={'user_id': request.user})
    # if post
    if request.method == 'POST':
        form = QuestionCreateForm(request.POST)
        # form.user_id = request.user
        if form.is_valid():
            form.save()
            # redirect to forum home
            return redirect("forum", page=1)
    # if get
    context = {'form': form}
    return render(request, 'forum/question_create.html', context)


@login_required(login_url='login')
def question_display(request, id):
    question = Question.objects.get(id=id)
    author = question.user_id
    current_user = request.user
    answers = question.answer_set.all()
    context = {
        'question': question,
        'answers': answers,
        'author': author,
        'current_user': current_user
    }
    return render(request, 'forum/question_display.html', context)


@login_required(login_url='login')
def question_update(request, id):
    question = Question.objects.get(id=id)
    if(request.user != question.user_id):
        return redirect("question_display", id=id)
    form = QuestionCreateForm(instance=question)
    if request.method == 'POST':
        form = QuestionCreateForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            # redirect to question page
            return redirect("question_display", id=id)
    context = {'form': form}
    return render(request, 'forum/question_create.html', context)


@login_required(login_url='login')
def question_delete(request, id):
    if request.method == 'POST':
        question = Question.objects.get(id=id)
        if(request.user != question.user_id):
            return redirect("question_display", id=id)
        question.delete()
        return redirect('forum', page=1)
    else:
        raise Http404("page not found")

#
# answer crud
#


@login_required(login_url='login')
def answer_create(request, question_id):
    form = AnswerCreateForm(
        initial={'question_id': question_id, 'user_id': request.user})
    # if post
    if request.method == 'POST':
        form = AnswerCreateForm(request.POST)
        if form.is_valid():
            form.save()
            # redirect to forum home
            return redirect("question_display", id=question_id)
    # if get
    context = {'form': form}
    return render(request, 'forum/answer_create.html', context)


@login_required(login_url='login')
def answer_update(request, answer_id):
    answer = Answer.objects.get(id=answer_id)
    if(request.user != answer.user_id):
        return redirect("question_display", answer_id=answer.question_id)
    form = AnswerCreateForm(instance=answer)
    if request.method == 'POST':
        form = AnswerCreateForm(request.POST, instance=answer)
        if form.is_valid():
            form.save()
            # redirect to question page
            return redirect("question_display", id=answer.question_id.id)
    context = {'form': form}
    return render(request, 'forum/answer_create.html', context)


@login_required(login_url='login')
def answer_delete(request, answer_id):
    if request.method == 'POST':
        answer = Answer.objects.get(id=answer_id)
        current_question_id = answer.question_id.id
        if(request.user != answer.user_id):
            return redirect("question_display", id=current_question_id)
        answer.delete()
        return redirect('question_display', id=current_question_id)
    else:
        print("invalid access")
        raise Http404("page not found")
