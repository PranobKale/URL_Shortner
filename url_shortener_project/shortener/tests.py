from django.test import TestCase
from django.urls import reverse
from .models import URL
import datetime
from django.utils.timezone import now

class URLShortenerTestCase(TestCase):
    
    def test_url_shortening(self):
        # Test POST request to shorten a URL
        data = {'url': 'https://www.example.com', 'expiry': '24'}
        response = self.client.post(reverse('shorten'), data)

        # Ensure the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Ensure the shortened URL is returned
        self.assertContains(response, 'https://short.ly/')
        
        # Ensure the URL is saved in the database
        url_obj = URL.objects.get(original_url='https://www.example.com')
        self.assertEqual(url_obj.original_url, 'https://www.example.com')
        
        # Ensure expiration timestamp is set correctly
        self.assertTrue(url_obj.expiration_timestamp > now())


class URLRedirectTestCase(TestCase):

    def setUp(self):
        # Set up a URL in the database
        self.original_url = 'https://www.google.co.in/'
        self.url_obj, created = URL.objects.get_or_create(
            original_url=self.original_url,
            shortened_url='abcd12', 
            expiration_timestamp=datetime.datetime.now() + datetime.timedelta(hours=24)
        )
        
    def test_redirect_to_original(self):
        # Test that accessing the shortened URL redirects to the original URL
        response = self.client.get(reverse('redirect_to_original', args=[self.url_obj.shortened_url]))
        
        # Check that the response redirects to the original URL
        self.assertRedirects(response, self.original_url)
        
    def test_redirect_expired_url(self):
        # Test redirect behavior for an expired URL
        expired_url,created = URL.objects.get_or_create(
            original_url='https://www.naukri.com/registration/createAccount?othersrcp=23531&wExp=N&utm_source=google&utm_medium=cpc&utm_campaign=Brand_Misspellings&gad_source=1&gclid=Cj0KCQiAhbi8BhDIARIsAJLOlufu6yzOtYkNyY8ylfeMMD0MqPvXQ5tK2EwD8X0O3nzzEDdigGCg5L8aAi0xEALw_wcB&gclsrc=aw.ds',
            shortened_url='abcd12',
            expiration_timestamp=datetime.datetime.now() - datetime.timedelta(hours=1)
        )
        
        response = self.client.get(reverse('redirect_to_original', args=[expired_url.shortened_url]))
        
        # Ensure that expired URLs return a 410 Gone response
        self.assertEqual(response.status_code, 410)
        self.assertContains(response, 'The URL has expired.')
