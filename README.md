# inventory_management_system
A simple ERP system

angular and django-rest-framework
====

In this app we'll build a persistent ERP system. The backend and database will be handled by django. django rest framework will convert the tabled data to JSON and angular will bring the frontend magic.

### Clone the starter project

I made a [angular-drf starter project](git@github.com:jasonshark/django-drf-angular-starter-project.git). We're going to start from there and build out the todolist. Clone it and give it a new name

```
$ git clone https://github.com/dhananisangit/inventory_management_system.git
$ cd inventory

```

### Set up virtual environment

We do this so we install the packages locally instead of to your machine. Our project dependencies are specified in `requirements.txt`.

```
$ source ~/.bash_profile
$ mkvirtualenv venv
$ lsvirtualenv
$ cd bootstrap
$ pip install -r requirements.txt
```

### Launch server

```
$ ./manage.py migrate
$ ./manage.py runserver
```

This sets up our database and starts the server. Go to `localhost:8000`. Now angular and drf play nicely

![django on the right](http://i62.tinypic.com/2z3uvfb.png)

### Create Todo model

This is the same as creating a table in our database to hold all of the todos. Each todo will take up a row in the table. The model defines what the columns are going to be. For each todo we'll have a title, description and is_completed.

**models.py**
```
from django.db import models

class Location(models.Model):
    name         = models.CharField(max_length=254, unique=True, verbose_name='Name')
    building_id  = models.ForeignKey(Building, on_delete=models.PROTECT)

    def __unicode__(self):
        return unicode(self.name)

    def get_location_names(self):
        location_names = self.objects.only('name', flat=True)
        return part_names

    class Meta:
        verbose_name = 'Location'
```

Then make the migrations that turns the above python into a database table: 

```
$ ./manage.py makemigrations
$ ./manage.py migrate
```

Check that it worked by opening up the shell and adding a todo:

```
$ ./manage.py shell
>>> from code.models import Location
>>> Todo.objects.all()
[]
>>> first_todo = Location(title='first todo',description='a little bit softer now',is_completed='false')
>>> first_todo.save()
[<Todo: first todo>]
```

At first there's nothing, now it looks like we added a todo to the database. Really we want to display this in the browser as JSON so angular can play with it.

### Serialize to JSON

Create a LocationSerializer in a new file `serializers.py`. This will convert our data into json.

```
from rest_framework import serializers
from .models import Todo

class LocationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Location
		fields = ('name', 'building_id')
```

Now prep our views for rendering JSON:

```
from django.shortcuts import render
from rest_framework import viewsets
from models import Todo
from serializers import LocationSerializer

# routes automatically generated
class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


# Home route to send template to angular
def index(request):
    return render(request, 'base.html')
```

We use the [ModelViewSet](http://www.django-rest-framework.org/api-guide/viewsets/#modelviewset) which automatically provides us endpoints for `.list()`, `.retrieve()`, `.create()`, `.update()`, and `.destroy()`. This is where DRF magic really happens. With that small class above we have the views necessary to create, read, update and delete todos. In the router we're going to map these out.

Update our routes in `urls.py`. These will define where and what JSON should be displayed.

```
from django.conf.urls import patterns, include, url
from rest_framework import routers
from . import views

app_router = routers.DefaultRouter()
app_router.register(r'todos', views.LocationViewSet, base_name='todos')

urlpatterns = [
    # Send base.html to angular
    url(r'^$', views.index, name='index'),

    url('^api/', include(app_router.urls)),
]
```

Hit `http://localhost:8000/api/location` in your browser and you'll see a JSON array of Todo objects in the nice DRF console. There are buttons for creating (using PUT requests), updating (PUT requests) and deleting (DELETE requests).


### Hook this up to the frontend

We are going to go a bit quick over the angular stuff because there's a full functional API.

First define the routes and a constant for our API endpoint.

```
var app = angular.module('ims', [
    'ui.router'
]);

app.constant('BASE_URL', 'http://localhost:8000/api/location/');

app.config(function($stateProvider, $urlRouterProvider){
    $stateProvider
        .state('home', {
            url: '/',
            templateUrl: '/static/templates/home.html',
            controller: 'MainCtrl'
        })
        .state('add-location', {
            url: "/addlocation",
            templateUrl: 'static/templates/add_location.html',
            controller: 'MainCtrl'
        });

    $urlRouterProvider.otherwise('/');
});
```

Special note, we are using [ui-router](https://github.com/angular-ui/ui-router). Also, make sure you have trailing slashes on your urls when making requests to DRF. The trailing slash had us stumped for a bit.

```
// will break without slash at the end
app.constant('BASE_URL', 'http://localhost:8000/api/location/');
```

Then define a service that makes requests to DRF and returns promises. We probably could have used [$resource](https://docs.angularjs.org/api/ngResource/service/$resource) or [Restangular](https://github.com/mgonto/restangular) here but I am not very familiar with them and do not know if they will survive in Angular 2.0. $http is simple and straight forward. Make http requests and return promises.

```
app.service('Location', function($http, BASE_URL){
    var Location = {};

    Location.all = function(){
        return $http.get(BASE_URL);
    };

    Location.update = function(updated){
        return $http.put(BASE_URL + updated.id, updated);
    };

    Location.delete = function(id){
        return $http.delete(BASE_URL + id + '/');
    };

    Location.addOne = function(new){
        return $http.post(BASE_URL, new)
    };

    return Todos;
});
```

Call the service methods in the controller:

```
app.controller('MainCtrl', function($scope, Location, $state){
    $scope.new = {};
    $scope.add = function() {
        Location.addOne($scope.new)
            .then(function(res){
                // redirect to homepage once added
                $state.go('home');
            });
    };

    $scope.toggleCompleted = function(todo) {
        Location.update(todo);
    };

    $scope.deleteLocation = function(id){
        Location.delete(id);
        // update the list in ui
        $scope.location = $scope.location.filter(function(location){
            return location.id !== id;
        })
    };

    Location.all().then(function(res){
        $scope.location = res.data;
    });
});
```



### Add add the markup

**/static/templates/home.html**
```
<div class='row text-center'>
    <div class='col-sm-4 col-sm-offset-4'>
        <h1>All Location</h1>

        <button ui-sref="add-location" class='btn btn-primary btn-lg' style='margin-bottom:20px;'>Add Location</button>

        <ul class="list-group">
            <li ng-repeat='l in location' ng-class="{completed: l.is_completed}" class="list-group-item">
                <input type="checkbox" ng-checked="l.is_completed" ng-change="toggleCompleted(l)" ng-model='l.is_completed'>  {{l.title}}

                <span class='badge' ng-click="deleteLocation(l.id)">X</span>
            </li>
        </ul>
    </div>
</div>
```

The markup will `ng-repeat` over the todos. [ng-change](https://docs.angularjs.org/api/ng/directive/ngChange) is a nifty directive that executes a function when whatever you pass to it is updated or changed. I stole this from the [Angular.js TodoMVC](https://github.com/tastejs/todomvc/tree/gh-pages/examples/angularjs) implementation. [ng-checked](https://docs.angularjs.org/api/ng/directive/ngChecked) will check the checkbox based on the truthy or falsey value we pass to it. [ng-class](https://docs.angularjs.org/api/ng/directive/ngClass) is also kind of cool. [scotch.io](https://scotch.io/tutorials/the-many-ways-to-use-ngclass) has a tutorial there about the many ways to use ngClass.

