
Overview

Eeeh no, this project is not about smartwatches. I have a nobler objective to assign to you: save the world. Time may be running out. So, ready? Go!

Near-Earth Objects (NEOs) are asteroids or comets (Small Solar System Bodies, to put it poetically) whose calculable trajectories may bring them close to Earth’s orbit. But how close? Who really wants to end up like the dinosaurs or in a Lars von Trier movie? No one, right? Therefore, I am certain you will have no objection to creating an application that can monitor the NEOs catalogued by NASA, by querying, through a judiciously chosen API, the data that this agency makes available to everyone.
Basic features

More specifically, this application should include the following features

    F1 : Manage users and access. Access to the application will be secured. There will be two types of users. Regular users, who will have to create an account (login + password) to be able to connect to the application, use its features and their personal space (see below), and administrators, special users who will be able to manage other users’ accounts, view the connection history, and choose to update NEO-Watch’s data using NASA’s API.
    F2 : Provide users with a dashboard. The user will have a dashboard, presenting for example the next NEOs passing close to Earth, the number of potentially dangerous NEOs among the upcoming approaches, the NEO closest to Earth over a given period, and all sorts of information that you consider relevant. This dashboard will be somewhat personalized, notably by displaying the user’s favorite NEOs (see F5), etc.
    F3 : Browse NEOs. The user will be able to search for one or more NEOs, according to criteria such as its name, identifier, dimensions, date of its next passage, etc. For each NEO viewed, you will display all characteristics that seem relevant. Sorting according to different criteria will be offered, as well as an export of the results in a format of your choice.
    F4 : Create a NEO. The user who observes it will be able to add a NEO to the API’s database. Care must be taken to ensure that created NEOs are not overwritten during successive updates of this database with data from NASA’s API.
    F5 : Manage a favorites list. The user will be able to add or remove NEOs from a viewable favorites list. For each NEO on this list, a history of its distance from Earth will in particular be kept, and may be used to produce exportable graphs.
    F6 : Create alerts. The user will be able to define alerts, centered on NEOs or not, such as: « Notify me when an asteroid more than 100 meters in size passes within 5 million kilometers of Earth ». If the application detects such events, a notification will be sent to the user when they log in.

Optional features

    FO1 : Compare several NEOs. The user will be able to select several asteroids and compare their characteristics (size, speed, distance from Earth, passage date, danger level, etc.). This comparison may be presented as a table or an exportable graph.
    FO2 : Keep search history. Each user will be able to view their search history for the last 30 days. In addition, administrators will be able to view the histories of users of their choice. Each search will therefore result in a record containing, at a minimum, the author, timestamp and asteroid concerned.
    FO3 : Build some statistics. The user will be able to access statistics such as the number of asteroids observed per month, size distribution, evolution in the number of approaches, average distance from Earth, proportion of objects classified as potentially dangerous, etc. The statistics must be relevant and justified.
    FO4 : Suggest an interesting NEO. The application will recommend to the user a selection of NEOs that could be particularly interesting to observe, based on explicit criteria of interest, which could, for example, combine size, distance, speed, rarity of passage, potentially dangerous nature, etc.
    FO5 : Communicate. The application will allow users and administrators to communicate by email. The former may, for example, report a bug to the latter, or inform them of a connection problem. The latter may notify them of the deletion of their account, regularly send them their statistics, etc.
    FO6 : Propose modifying a NEO. Why not, right? The user, an amateur astronomer, will be able to propose modifying certain data relating to a NEO. The administrator will be notified of the proposed modifications (and the process will stop there, alas, since there is no question of modifying NASA’s data via the API that it so graciously makes available to us!)
    FO7 : Automatically reload the data. For those interested in the concept of batch processing, you can develop an automatic reloading of the API database from the data made available by NASA’s API. This reloading would replace the administrator’s manual action.
    FO8 : Make people dream a little. Since everything is not just anxiety and destruction, and since the sky has always made people dream, the application will allow the user to export the picture of the day, which NASA provides via a dedicated API.

Advice / Tools

Tools:

    Language : Python
    Version control tool : Git
    Database : PostgreSQL
    Backend API : FastAPI
    Frontend : in python (streamlit, tkinter, reflex, etc.) or HTML/JS/CSS (React, Vue, etc.)
    Tests : pytest

