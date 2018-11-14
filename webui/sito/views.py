from django.shortcuts import render

def home(request):
    return render(request, 'sito/brand.html')

def community(request):
    return render(request, 'sito/community.html')

def CommunityDetail(request):
    # print (category)
    return render(request, 'sito/community-detail.html')
