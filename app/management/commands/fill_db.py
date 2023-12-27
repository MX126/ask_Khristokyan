from django.core.management import BaseCommand
from faker import Faker
from django.contrib.auth.models import User
import random

from app.models import Question, Answer, Profile, Tag, Vote

fake = Faker()


class Command(BaseCommand):
    help = "Fills database with fake data for your models"

    def add_arguments(self, parser):
        parser.add_argument("num", type=int)

    def handle(self, *args, **kwargs):
        num = kwargs['num']
        questions_amount = num * 10

        self.stdout.write(self.style.SUCCESS('Parsing - DONE'))

        # Create fake tags
        tags = []
        tag_names = set()
        for _ in range(num):
            while True:
                name = fake.word() + str(fake.random_int(min=0, max=num - 1))
                if name not in tag_names:
                    break

            tag_names.add(name)
            tags.append(Tag(name=name))

        self.stdout.write(self.style.SUCCESS('tags - DONE'))

        Tag.objects.bulk_create(tags)

        self.stdout.write(self.style.SUCCESS('Tag objects - DONE'))

        # Create fake users
        users = []
        user_usernames = set()
        for _ in range(num):
            while True:
                username = fake.user_name()
                if username not in user_usernames:
                    break
            email = fake.email()
            password = fake.password()

            user_usernames.add(username)
            users.append(User(username=username, email=email, password=password))

        self.stdout.write(self.style.SUCCESS('users - DONE'))

        User.objects.bulk_create(users)

        self.stdout.write(self.style.SUCCESS('User objects - DONE'))

        users = User.objects.all()

        # Create fake user profiles
        profiles = [
            Profile(user=users[i])
            for i in range(num)
        ]

        self.stdout.write(self.style.SUCCESS('profiles - DONE'))

        Profile.objects.bulk_create(profiles)

        self.stdout.write(self.style.SUCCESS('Profile objects - DONE'))

        # Create fake questions, votes and answers for them
        questions = []
        votes = []
        answers = []
        for i in range(questions_amount):
            user = users[fake.random_int(min=0, max=num - 1)]
            title = fake.sentence(nb_words=6)
            content = fake.paragraph()
            created_at = fake.date_between(start_date='-1y', end_date='today')
            total_votes = 10

            question = Question(user=user, title=title, content=content, created_at=created_at, total_votes=total_votes)

            user_usernames = set()
            for _ in range(15):
                while True:
                    user = users[fake.random_int(min=0, max=num - 1)]
                    username = user.username
                    if username not in user_usernames:
                        break
                user_usernames.add(username)
                votes.append(Vote(user=user, question=question, answer=None, value=1))

            for _ in range(5):
                while True:
                    user = users[fake.random_int(min=0, max=num - 1)]
                    username = user.username
                    if username not in user_usernames:
                        break
                user_usernames.add(username)
                votes.append(Vote(user=user, question=question, answer=None, value=-1))

            user_usernames_for_answers = set()
            for _ in range(10):
                while True:
                    user = users[fake.random_int(min=0, max=num - 1)]
                    username = user.username
                    if username not in user_usernames_for_answers:
                        break
                user_usernames_for_answers.add(username)

                content = fake.paragraph()
                created_at = fake.date_between(start_date=question.created_at, end_date='today')
                status = fake.random_element(elements=('c', 'i'))
                answers.append(
                    Answer(user=user, question=question, content=content, created_at=created_at, status=status))

            questions.append(question)

            self.stdout.write(self.style.ERROR(f'{i} questions - DONE'))

        self.stdout.write(self.style.SUCCESS('questions, votes, answers - DONE'))

        Question.objects.bulk_create(questions)

        self.stdout.write(self.style.SUCCESS('Question objects - DONE'))

        Vote.objects.bulk_create(votes)

        self.stdout.write(self.style.SUCCESS('Vote objects - DONE'))

        Answer.objects.bulk_create(answers)

        self.stdout.write(self.style.SUCCESS('Answer objects - DONE'))

        questions = Question.objects.all()

        tags = list(Tag.objects.all())

        self.stdout.write(self.style.SUCCESS('Getting Question and Tag objects - DONE'))

        # Add tags to questions
        for i in range(questions_amount):
            amount_of_tags_to_set = fake.random_int(min=1, max=6)
            random_tags = random.sample(tags, amount_of_tags_to_set)
            questions[i].tags.set(random_tags)
            self.stdout.write(self.style.ERROR(f'{i} tags set - DONE'))

        self.stdout.write(self.style.SUCCESS('Tags set - DONE'))

        self.stdout.write(self.style.SUCCESS(f"Successfully populated the database with fake data with ratio = {num}."))
