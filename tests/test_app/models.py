from django.db import models


class User(models.Model):
    email = models.EmailField(max_length=254)

    def __str__(self):
        return '(User #{0}: {1})'.format(self.pk, self.email)


    def __repr__(self):
        return '(User #{0}: {1})'.format(self.pk, self.email)


class Author(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    publishing_name = models.CharField(max_length=25, blank=True, null=True)
    age = models.IntegerField()

    def __str__(self):
        return '(Author #{}: {})'.format(self.pk, self.publishing_name)

    def __repr__(self):
        return '(Author #{}: {})'.format(self.pk, self.publishing_name)
