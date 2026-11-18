import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from tournaments.models import Tournament

def home(request):
    tournaments = Tournament.objects.filter(status='PUBLISHED').order_by('start_at')[:6]
    return render(request, 'core/home.html', {'tournaments': tournaments})

def manifest(request):
    data={'name':'ROOM ARENA','short_name':'ROOM ARENA','start_url':'/','display':'standalone','background_color':'#090d14','theme_color':'#ff5a36','description':'Community Clash Squad tournament hub','icons':[{'src':'/static/pwa/icon-192.png','sizes':'192x192','type':'image/png'},{'src':'/static/pwa/icon-512.png','sizes':'512x512','type':'image/png'}]}
    return JsonResponse(data)

def service_worker(request):
    js="const CACHE='room-arena-v1';const ASSETS=['/','/static/css/site.css','/static/js/app.js'];self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS))));self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))));self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;e.respondWith(caches.match(e.request).then(hit=>hit||fetch(e.request).catch(()=>caches.match('/'))))});"
    return HttpResponse(js, content_type='application/javascript')
