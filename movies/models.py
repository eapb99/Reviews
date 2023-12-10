from django.db import models


class Movie(models.Model):
    productid = models.CharField(db_column='productId', primary_key=True)  # Field name made lowercase.
    name = models.CharField()

    class Meta:
        managed = False
        db_table = 'movie'


class ReviewPartitioned(models.Model):
    id = models.IntegerField(
        primary_key=True)  # The composite primary key (id, year) found, that is not supported. The first column is selected.
    productid = models.CharField(db_column='productId')  # Field name made lowercase.
    userid = models.CharField(db_column='userId')  # Field name made lowercase.
    profilename = models.CharField(db_column='profileName')  # Field name made lowercase.
    helpfulness = models.CharField()
    score = models.FloatField()
    time = models.DateTimeField()
    summary = models.CharField()
    text = models.CharField()
    year = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'review_partitioned'
        unique_together = (('id', 'year'),)


class User(models.Model):
    userid = models.CharField(db_column='userId', primary_key=True)  # Field name made lowercase.
    name = models.CharField()

    class Meta:
        managed = False
        db_table = 'user'
