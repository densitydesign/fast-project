import json, pprint, random, requests
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse

def home(request):
    return render(request, 'sito/brand.html', {'section':'brand'})


def community_definition(request):
    if request.method == 'POST':
        # Per il momento mettiamo gli id in sessione
        request.session['community_id'] = request.POST.getlist('community_id')
        return HttpResponseRedirect(reverse('community'))
    url = 'http://localhost:8080/communities'
    response = requests.get(url)
    elenco = []
    if (response.ok):
        data = json.loads(response.content)
        for d in data:
            d['id'] = '%d' %d['id']
            elenco.append(d)
    # TODO: gestire nomi custom
    return render(request, 'sito/community_definition.html', {'section':'community', 'elenco': elenco})

def community(request):
    community_ids = ','.join(request.session.get('community_id', []))
    url = 'http://localhost:8080/communities/graph?communities=%s&limit=10'% community_ids
    response = requests.get(url)
    edges = []
    nodes = []
    if (response.ok):
        data = json.loads(response.content)
        for d in data['edges']:
            edges.append(d)

        # Trovo il numero massimo di post per poter dimensionare i nodi
        maxPosts = 0 
        for d in data['nodes']:
            p = d.get('num_posts', 1)
            if p > maxPosts:
                maxPosts = p

        for d in data['nodes']:
            if d['id'][0] == 'u':
                d['color'] = '#c6efef'
            else:
                d['color'] = "#C7BBD5" 
            d['size'] = (d.get('num_posts', maxPosts) / maxPosts) * 100
            nodes.append(d)
        random.shuffle(nodes)
    return render(request, 'sito/community.html', {'section':'community', 'edges': edges, 'nodes':nodes})

def community_detail(request, id_community):
    # print (category)
    return render(request, 'sito/community-detail.html', {'section':'community'})


def change_section(request):
    if request.POST.get('switch', '') == 'community':
        return HttpResponseRedirect(reverse('community-definition'))
    return HttpResponseRedirect(reverse('brand'))
