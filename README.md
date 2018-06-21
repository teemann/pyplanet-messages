# Messages
This is an app for pyplanet that enables you to show arbitrary messages on the screen. Those messages can be
in the form of
 * Text (formatted using $...)
 * Images
 * Custom partial manialinks
 
At some point, support for periodic chat messages will be added.
 
Text and Images can also link to a website (e.g. Discord link). Of course, custom manialinks also support this feature,
you will need to add it to your manialink though.

## Installation
To install this app, you can either download a ZIP-File of this repository or you can also clone the repository.
It is recommended to create a directory `teemannTest` next to `manage.py`. Next, enter the just created directory.
Now you can choose between the two installation methods. It is recommended to use `Git clone`, since it makes
updating a lot easier (just a simple `git pull`).

#### Git clone
Then, in this directory, run

```git clone https://github.com/teemann/pyplanet-messages.git```

Rename the directory from `pyplanet-messages` to `messages`.

#### ZIP-File
Download the ZIP-File of this repository from [here](https://github.com/teemann/pyplanet-messages/archive/master.zip).
Unzip the ZIP-File into the directory `teemannTest`. Now, rename the folder `pyplanet-messages-master` to `messages`.

#### apps.py
The last step of the installation process is to add the app to `apps.py`. To do this, just open the file and add the
line

```'teemannTest.messages',```

underneath the other apps. Make sure to use the same indentation as in the lines before. After a restart of pyplanet,
the messages app is ready to be used.


## Configuration
To access the messages dialog, type `//messages` in the chat (only admin). You will then see a dialog similar
to this:

![img1]

The two columns in this table are
 * Type
 * Name

which can both be configured in the [configuration dialog](#configuring-a-message).

### Adding a new message
To add a new message, click the `New` Button (top-right). This will open another dialog, which is 
described [here](#configuring-a-message).

### Editing an existing message
To edit a message, click the small cog icon for the message. This will open the same dialog that will be opened by
clicking `New`, but it will be filled with the data that was saved before.

### Deleting a message
To delete a message, use the small trashcan icon. When clicked, you will be asked if you are sure.  
*__Warning:__ Once deleted, the message cannot be restored.*

### Configuring a message
The configuration dialog for messages looks like this:

![img2]

#### Name
A message should have a name, so you can easily identify it in the messages dialog.

#### Position
Specifies the position where the message should be shown. The coordinates are the same as used by manialinks.
`X` goes from `-160` to `160` (left to right), `Y` goes from `-90` to `90` (bottom to top). `Z` can be an arbitrary
value.  
*__Note:__ Currently, all messages are displayed on top of the other widgets of pyplanet. `Z` can be used to specify
the Z-Order of messages only.*  
*__Note:__ This value is not used if type is `XML`.*

#### Value
This is the value of the message. If the type is `Text`, this is the text that will be shown. Multiple lines are
supported. Formatting is also supported. If the type is `Image`, this is a URL to an Image that should be shown.
If the type is `XML`, this is a manialink. Internally this will then be wrapped by `<frame></frame>`.

#### Type
This can be
 * Text
 * Image
 * XML
 
See [Value](#value) for an explanation.  
*__Note:__ When using `Image` you might have to rejoin the server to see the image.*

#### Link
This is only used if the type is either `Text` or `Image`.  
Specifies a link that will be opened when a player clicks on the message.  
*__Note:__ When a player uses the Steam version of the game and the links starts with `http(s)://`, the
link will be opened in the Steam-overlay browser. If `http(s)://` is omitted, the link will be opened in the
standard browser (e.g. Chrome).*

#### Size
This option is only shown and used if the selected type is `Image`.

![img3]

Here you can specify the preferred size of the image (in manialink units, so 320x180 equals the size of the screen).  
The option `Keep aspect ratio` can be disabled, so the image will be distorted if the wrong dimensions are used.


[img1]: https://teemann.github.io/images/messages/msg1.png?
[img2]: https://teemann.github.io/images/messages/msg2.png?
[img3]: https://teemann.github.io/images/messages/msg3.png?