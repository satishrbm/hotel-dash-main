Dasshboard Add-on made using Vue and Python

# Structure

```
Project Root
├── .addons.yml              # Configuration file for managing addon
├── .github
│   └── workflows
│       └── build-push.yml   # GitHub Actions workflow for building and pushing the project
├── dash
│   ├── .gitignore
│   ├── .main
│   ├── Dockerfile           # Instructions for building a Docker image for the project
│   ├── Migration.md         # Documentation for migrating the project repository
│   ├── build.yaml           # Build configuration file
│   ├── changelog.md
│   ├── config.yaml          # Main configuration file for the project
│   ├── controllers
│   │   ├── app.py           # Main application controller logic
│   │   └── ha.py            # Home Assistant Websocket connection logic
│   ├── docker-compose.yml   # Docker Compose file
│   ├── helpers
│   │   └── app.py           # Helper functions for the application
│   ├── icon.png
│   ├── logo.png
│   ├── main.py              # Entry point of the Python application
│   ├── run.sh               # Shell script to run the application
│   ├── src
│   │   ├── css
│   │   │   └── app.css      # Main stylesheet for the application
│   │   └── js
│   │       ├── App.old.vue  # Deprecated version of the main Vue component
│   │       ├── App.vue      # Main Vue.js application component
│   │       ├── Pages
│   │       │   ├── Home.vue # Vue component for the home page
│   │       │   └── Login.vue # Vue component for the login page
│   │       ├── app.js       # Main JavaScript file for the application
│   │       ├── components
│   │       │   ├── Error.vue # Vue component for displaying error messages
│   │       │   ├── FS.vue    # Vue component
│   │       │   ├── Loader.vue # Vue component for loading animations
│   │       │   ├── Placeloader.vue # Vue component for placeholder content during loading
│   │       │   ├── SceenSaver.vue # Vue component for screen saver functionality
│   │       │   ├── Waite.vue # Vue component for wait/loader functionality
│   │       │   └── confirm.vue # Vue component for confirmation dialogs
│   │       ├── mixins
│   │       │   └── app.js    # JavaScript mixins to be used in Vue components
│   │       ├── request.js    # JavaScript file for handling HTTP requests
│   │       ├── router.js     # JavaScript file for managing routes in the Vue.js application
│   │       └── store.js      # JavaScript file for managing the Vuex store (state management)
│   ├── static
│   │   ├── css
│   │   │   └── app.css       # Static CSS file for the application
│   │   ├── favicon.ico
│   │   ├── images
│   │   │   └── Logo.png
│   │   ├── js
│   │   │   ├── 460.js
│   │   │   ├── 460.js.LICENSE.txt
│   │   │   ├── 65.js
│   │   │   ├── 65.js.LICENSE.txt
│   │   │   ├── 995.js
│   │   │   ├── 995.js.LICENSE.txt
│   │   │   ├── app.js
│   │   │   └── app.js.LICENSE.txt
│   │   └── template.txt
│   ├── storage
│   │   ├── auth.json         # JSON file for storing authentication data
│   │   ├── entities.json     # JSON file for storing entities and states data to update frontend
│   │   ├── log.json          # JSON file for storing logs
│   │   └── secure.json       # JSON file for securely storing device id data
│   └── templates
│       └── pages
│           └── index.html    # HTML template for the main page
└── repository.json           # JSON file for storing repository-related data
```