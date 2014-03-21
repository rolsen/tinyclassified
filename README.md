TinyClassified
==========
A no-frills embeddable mix between professional portfolios and lightweight job boards.

 - Directory listings for companies or people doing a thing
 - Geocoding and tagging / categorizing those listings
 - Jobs board that complements those directory listings



Contact / development team
--------------------------
This is a project of [Gleap LLC](http://gleap.org) with copyright 2014.

 - Sam Pottinger ([samnsparky](http://gleap.org/))
 - Rory Olsen ([rolsen](https://github.com/rolsen))


Technologies used
-----------------
FollowThru uses a standard set of Python libraries and frameworks common to web application development including:

 - [MongoDB](http://www.mongodb.org/)
 - [Flask](http://flask.pocoo.org/)
 - [Backbone.js](http://backbonejs.org/)
 - [pymox](https://code.google.com/p/pymox/) (server-side testing)


Local system setup
------------------
Ensure Python 2.7.*, PIP, and MongoDB.

 - Python: [Mac](http://docs.python-guide.org/en/latest/starting/install/osx/) (brew is suggested), [Linux](http://docs.python-guide.org/en/latest/starting/install/linux/), [Windows](http://www.python.org/)
 - PIP: [Mac](http://stackoverflow.com/questions/17271319/installing-pip-on-mac-os-x), [Linux](http://docs.python-guide.org/en/latest/starting/install/linux/), [Windows](http://stackoverflow.com/questions/4750806/how-to-install-pip-on-windows)
 - MongoDB: [All platforms](http://www.mongodb.org/downloads)


Local virtual environment setup
-------------------------------
Install VirtualEnv
```$ easy_install pip```

Create virtual environment
```$ virtualenv venv```

Start virtual environment
```$ source venv/bin/activate```

Install software
```$ pip install -r requirements.txt```

Leave virtual environment
```$ deactivate```


Local development / testing
---------------------------
Start virtual environment
```$ source venv/bin/activate```

Run automated tests
```$ python run_tests.py```

Start local server
```$ python tiny_classified.py```

Leave virtual environment
```$ deactivate```


Development guidelines / standards
----------------------------------
Due to the potential for mutliple deployment and client-driven modification outside of Gleap (the original developer), this project values high test coverage and style adherence.

 - The project asks for 80% test coverage on server-side. Models do not count towards or against that 80% requirement.
 - Server-side modules, classes, and functions should be documented using [epydoc](http://epydoc.sourceforge.net/).
 - Server-side code should conform to [Google's Python Style Guide](http://google-styleguide.googlecode.com/svn/trunk/pyguide.html).
 - The project uses plain old CSS but should have element, class, and finally ID-based rules in that order.
 - Client-side JS should follow [Google's JavaScript Style Guide](http://google-styleguide.googlecode.com/svn/trunk/javascriptguide.xml).
 - Client-side files, classes, and functions should be documented using [JSDoc](http://usejsdoc.org/).
 - Client-side automated tests are optional but encouraged. For help with getting started on client-side testing, see [Addy Osmani's tutorial](http://addyosmani.com/blog/unit-testing-backbone-js-apps-with-qunit-and-sinonjs/).
 - All code checked in (via Gleap) to master or a version release branch should go through code review.
 - Code produced during pair programming or for initial project bootstrapping does not require code review. However, the results of pair programming should still go through a pull request.
 - Engineers can perform a code review for themselves if another enigneer is not available within one working day.
