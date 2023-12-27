from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta


class QuestionManager(models.Manager):
    def tagged(self, tag_name):
        return self.filter(tags__name=tag_name)

    def get_hot_questions(self):
        today = date.today()
        # first_day = date(today.year, today.month - 1, 1)
        # last_day = date(today.year, today.month, 1)
        first_day = today - timedelta(days=50)
        last_day = today

        return self.filter(created_at__range=[first_day, last_day])

    def get_top_questions(self, count=10):
        return self.order_by('-total_votes')[:count]

    def get_question_by_id(self, question_id):
        return Question.objects.get(pk=question_id)


class ProfileManager(models.Manager):
    def get_profile_by_id(self, user_id):
        return Profile.objects.get(user_id=user_id)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True, default="avatar.jpeg")

    objects = ProfileManager()

    def __str__(self):
        return self.user.username


class VoteManager(models.Manager):
    def create_or_update_vote(self, user, question=None, answer=None, value=0):
        # Check if the user has already voted on the question or answer
        existing_vote = self.filter(user=user, question=question, answer=answer).first()

        if existing_vote:
            # If the user has already voted, update the existing vote
            # existing_vote.value = value
            # existing_vote.save()
            # return existing_vote
            existing_vote.delete()
        else:
            # If the user hasn't voted yet, create a new vote
            return self.create(user=user, question=question, answer=answer, value=value)

    def get_question_score(self, question):
        # Calculate the score for a given question
        upvotes = self.filter(question=question, value=1).count()
        downvotes = self.filter(question=question, value=-1).count()
        score = upvotes - downvotes
        return score


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE, null=True, blank=True)
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE, null=True, blank=True)
    value = models.IntegerField()
    objects = VoteManager()

    def __str__(self):
        return f"'{self.user.username}' voted on '{self.question.title}'"


class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    content = models.TextField()
    tags = models.ManyToManyField('Tag', related_name='questions')
    created_at = models.DateField(default=date.today())
    # total_votes = models.IntegerField(default=0)

    objects = QuestionManager()

    def __str__(self):
        return self.title


class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    created_at = models.DateField(default=date.today())
    # total_votes = models.IntegerField(default=0)

    STATUS_CHOICES = [
        ('c', 'correct'),
        ('i', 'incorrect'),
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='i')

    # objects = AnswerManager()

    def __str__(self):
        return f"Answer to '{self.question.title}' from '{self.user.username}'"


class Tag(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name
