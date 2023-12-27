from django.contrib import auth
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse
from django.db.models import Sum

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from app.forms import LoginForm, RegisterForm, SettingsForm
from app.models import Question, Profile, Vote


def paginate(objects_list, request, per_page=5):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        raise Http404("Page not found")
    return page_obj


@login_required(login_url='login/', redirect_field_name='continue')
def index(request):
    # questions = Question.objects.all()
    questions = Question.objects.annotate(totaly_votes=Sum('vote__value'))

    context = {
        'page_obj': paginate(questions, request),
        # 'question_votes': {question.id: Question.objects.count_total_votes(question.id) for question in questions},
    }
    return render(request, 'index.html', context)


@csrf_protect
def log_in(request):
    print(request.GET)
    print(request.POST)
    if request.method == 'GET':
        login_form = LoginForm()
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = authenticate(request, **login_form.cleaned_data)
            print(user)
            if user is not None:
                login(request, user)
                print('Successfully logged in')
                return redirect(request.GET.get('continue', '/'))
            else:
                login_form.add_error(None, 'Wrong password or user does not exist')
    return render(request, 'login.html', context={'form': login_form})


def logout(request):
    auth.logout(request)
    return redirect(reverse('login'))


@login_required(login_url='login/', redirect_field_name='continue')
def ask(request):
    return render(request, 'ask.html')


@csrf_protect
def signup(request):
    print(request.GET)
    print(request.POST)
    if request.method == 'GET':
        register_form = RegisterForm()
    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user = register_form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            profile = Profile(user=user)
            profile.save()
            print(user)
            if user is not None:
                # login(request, user)
                print('Successfully signed up')
                return redirect(reverse('index'))
            else:
                register_form.add_error(None, 'Registration error')
    return render(request, 'signup.html', context={'form': register_form})


@csrf_protect
@login_required(login_url='login/', redirect_field_name='continue')
def settings(request):
    if request.method == 'GET':
        settings_form = SettingsForm(initial=model_to_dict(request.user))
        return render(request, 'settings.html', context={'form': settings_form})

    elif request.method == 'POST':
        settings_form = SettingsForm(request.POST, request.FILES, instance=request.user)

        if settings_form.is_valid():
            settings_form.save()

    else:
        settings_form = SettingsForm()

    return render(request, 'settings.html', context={'form': settings_form})


@login_required(login_url='login/', redirect_field_name='continue')
def hot(request):
    # questions = Question.objects.all()
    questions = Question.objects.get_hot_questions().annotate(totaly_votes=Sum('vote__value'))

    context = {
        'page_obj': paginate(questions, request),
    }
    return render(request, 'hot.html', context)


@login_required(login_url='login/', redirect_field_name='continue')
def top(request):
    questions = Question.objects.get_top_questions().annotate(totaly_votes=Sum('vote__value'))

    context = {
        'page_obj': paginate(questions, request, 10),
    }
    return render(request, 'top.html', context)


@login_required(login_url='login/', redirect_field_name='continue')
def tag(request, tag_name):
    questions = Question.objects.tagged(tag_name).annotate(totaly_votes=Sum('vote__value'))
    context = {
        'tag': tag_name,
        'page_obj': paginate(questions, request),
    }
    return render(request, 'tag.html', context)


@login_required(login_url='login/', redirect_field_name='continue')
def question(request, question_id):
    if question_id > len(Question.objects.all()):
        raise Http404("Question does not exist")
    my_question = Question.objects.filter(pk=question_id).annotate(totaly_votes=Sum('vote__value')).first()
    answers = my_question.answers.all().annotate(totaly_votes=Sum('vote__value'))
    context = {
        'question': my_question,
        'page_obj': paginate(answers, request),
    }
    return render(request, 'question.html', context)


@csrf_protect
@login_required()
def question_upvote(request):
    question_id = request.POST.get('question_id')
    my_question = get_object_or_404(Question, pk=question_id)
    Vote.objects.create_or_update_vote(user=request.user, question=my_question, value=1)
    count = Vote.objects.get_question_score(my_question)

    return JsonResponse({
        'count': count
    })
