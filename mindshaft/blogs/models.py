from django.db import models
from django.utils.timezone import now

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    uploaded_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @staticmethod
    def add_blog(title, content, image=None):
        """
        Adds a new blog entry.
        """
        blog = Blog.objects.create(title=title, content=content, image=image)
        return blog

    def update_blog(self, title=None, content=None, image=None):
        """
        Updates the blog entry.
        """
        if title:
            self.title = title
        if content:
            self.content = content
        if image:
            self.image = image
        self.save()
        return self

    def delete_blog(self):
        """
        Deletes the blog entry.
        """
        self.delete()

    @staticmethod
    def filter_by_date(start_date, end_date):
        """
        Filters blogs between specific dates.
        """
        return Blog.objects.filter(uploaded_at__range=(start_date, end_date))
