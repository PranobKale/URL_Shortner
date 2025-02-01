from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse,HttpResponse
from .models import URL, AccessLog
from hashlib import md5
import datetime
from django.utils.timezone import now
import pytz
from urllib.parse import urlparse

def index(request):
    return render(request, 'shortener/index.html')
    # return HttpResponse("<h1> Hello $$$$ </h1>")


def shorten_url(request):
    """
    Shortens a given URL and stores it in the database with an expiration timestamp.

    Description:
    This function accepts a POST request containing an `original_url` and an optional `expiry` parameter
    (defaulting to 24 hours). It generates a unique shortened URL using an MD5 hash of the original URL.
    If the same original URL has already been shortened, it retrieves the existing shortened URL.
    The function returns a rendered HTML page displaying the shortened URL.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - A rendered HTML page with the shortened URL if the operation succeeds.
    - A JSON error response if there is an issue with the input or unexpected errors occur.
    """
    try:
        # Check if the request method is POST
        if request.method == 'POST':
            # Localize to Asia/Kolkata (IST)
            # IST = pytz.timezone('Asia/Kolkata')
            UTC = pytz.UTC

            global full_shortened_url
            # Extract the original URL and expiry time from the request
            original_url = request.POST.get('url')
            try:
                expiry_hours = int(request.POST.get('expiry'))  # Default expiry is 24 hours if not provided
            except:
                expiry_hours = 24
            
            
            # Validate the input URL
            if not original_url:
                raise ValueError("Original URL is required.")  # Raise an error if the URL is missing
            
            # Check if the URL is valid
            parsed_url = urlparse(original_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid URL provided.")  # Raise an error if the URL is not valid
            
            # Generate a unique hash for the URL
            hash_object = md5(original_url.encode())
            short_url = hash_object.hexdigest()[:6]  # Use the first 6 characters of the hash as the short code
            # Create or retrieve the URL object in the database
            url, created = URL.objects.get_or_create(
                original_url=original_url,
                defaults={
                    'shortened_url': short_url,  # Store the generated short URL
                    'expiration_timestamp': datetime.datetime.now(UTC) + datetime.timedelta(hours=expiry_hours)  # Set expiration
                }
            )

            if not created:
                # Check if the URL has expired
                if url.expiration_timestamp < datetime.datetime.now(UTC):
                    # URL has expired, update expiration timestamp
                    url.expiration_timestamp = datetime.datetime.now(UTC) + datetime.timedelta(hours=expiry_hours)
                    url.save()
                    message = "URL already exists. Expiration time has been extended."
                else:
                    message = "URL already exists and is still valid. No changes made."

            else:
                message = "New URL shortened successfully!"


            # Dynamically generate the full shortened URL using request.build_absolute_uri
            full_shortened_url = request.build_absolute_uri(f'/{url.shortened_url}/')

            data = {
                'shortened_url': full_shortened_url,  # Full shortened URL
                'shortened_url_code': url.shortened_url , # Shortened URL code for internal usage
                'message' : message
            }

            # Render the response using the 'shortened_url.html' template
            return render(request, 'shortener/shortened_url.html', context=data)

        else:
            # Handle non-POST requests
            return JsonResponse({'error': 'Invalid request method. Please use POST.'}, status=400)

    except ValueError as ve:
        # Handle validation errors (e.g., missing original URL)
        return JsonResponse({'error': str(ve)}, status=400)
    
    except Exception as e:
        # Handle all other unexpected exceptions
        return JsonResponse({'error': 'An unexpected error occurred.', 'details': str(e)}, status=500)

def redirect_to_original(request, short_url):
    """
    Redirects a shortened URL to its original URL.

    Parameters:
    - request: The HTTP request object.
    - short_url: The shortened URL code.

    Returns:
    - Redirects to the original URL or an appropriate error response.
    """
    try:
        # Fetch the URL object using the shortened URL
        url = get_object_or_404(URL, shortened_url=short_url)

        # Define Indian Standard Time (IST)
        # IST = pytz.timezone('Asia/Kolkata')
        UTC = pytz.UTC

       # Check if the URL has expired
        if url.expiration_timestamp < datetime.datetime.now(UTC):
            return HttpResponse("The URL has expired.", status=410)

        # Log the access for analytics, including the timestamp, IP address, and shortened URL

        # Get the current time in IST
        access_timestamp = datetime.datetime.now(UTC)

        AccessLog.objects.create(
            shortened_url=url,
            ip_address=request.META.get('REMOTE_ADDR'),
            access_timestamp=access_timestamp 
        )
        # Redirect to the original URL
        return redirect(url.original_url)
    except Exception as e:
        # Return a detailed error message if something goes wrong
        return HttpResponse(f"Error: Unable to redirect. Details: {e}, Short URL: {short_url}", status=404)


def analytics(request, short_url):
    """
    Provides analytics for a shortened URL.

    Parameters:
    - request: The HTTP request object.
    - short_url: The shortened URL code.

    Returns:
    - Renders the analytics page with URL access logs and details.
    """
    try:
        # Localize to Asia/Kolkata (IST)
        IST = pytz.timezone('Asia/Kolkata')

        # Fetch the URL object using the shortened URL
        url = get_object_or_404(URL, shortened_url=short_url)

        # Fetch access logs for the shortened URL
        logs = url.access_logs.all()

        # Dynamically generate the full shortened URL using request.build_absolute_uri
        full_shortened_url = request.build_absolute_uri(f'/{url.shortened_url}/')

        # Prepare data for rendering
        data = {
            'short_url': f'{full_shortened_url}',  # Full shortened URL
            'access_count': logs.count(),  # Total number of accesses
            'expiration_timestamp': url.expiration_timestamp.astimezone(IST).strftime("%d-%b-%Y %I:%M %p"),  # Format the timestamp in 12-hour format
            'original_url': url.original_url,  # Original URL
            'access_logs' : [
                {
                    'timestamp': log.access_timestamp.astimezone(IST).strftime("%d-%b-%Y %I:%M %p"),  # Format the timestamp in 12-hour format
                    'ip_address': log.ip_address
                }
                for log in logs
            ]# List of access log details
        }

        # Render the analytics page
        return render(request, 'shortener/analytics.html', context=data)
    except Exception as e:
        # Handle unexpected errors and return a detailed error response
        return JsonResponse(
            {'error': f"An error occurred while fetching analytics. Details: {e}"},
            status=500
        )
