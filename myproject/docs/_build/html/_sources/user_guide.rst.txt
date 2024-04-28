.. _user-guide:

User Guide
==========

This guide will help you get started with our Notes API. It covers the basics of creating an account, obtaining access, and interacting with the API endpoints.

Registering a New User
----------------------

To register as a new user, you will need to send a POST request to the `/auth/users/` endpoint with a JSON payload that includes your desired username and password.

.. code-block:: json

    {
      "username": "your_username",
      "password": "your_password"
    }

Logging In
----------

Once you have registered, you can log in by sending a POST request to the `/auth/token/login/` endpoint with the same username and password used during registration.

.. code-block:: json

    {
      "username": "your_username",
      "password": "your_password"
    }

If your credentials are correct, you will receive a response containing your authentication token.

.. code-block:: json

    {
      "auth_token": "your_token_here"
    }

Using the API
-------------

With the authentication token, you can now interact with the API.

- To **create** a note, send a POST request to `/notes/create/` with the note content. Include the token in the `Authorization` header.

.. code-block:: json

    {
      "title": "Note Title",
      "content": "Note Content"
    }

- To **retrieve** all notes, send a GET request to `/notes/`. No data payload is required.

- To **retrieve**, **update**, or **delete** a specific note, send a GET, PUT, or DELETE request respectively to `/notes/(note_id)/`. For PUT requests, include the new note content in the request body.

.. note::

   You can only update or delete notes that you have created.

Remember to always include the `Authorization: Token <your_token_here>` header in your requests after logging in.

Logging Out
-----------

To log out and invalidate your current token, send a POST request to `/auth/token/logout/`. This action will require your current authentication token in the header.
