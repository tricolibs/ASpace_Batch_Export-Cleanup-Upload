# ArchivesSpace & XTF Program - DEV
![homepage-ead-001](https://user-images.githubusercontent.com/62658840/81198762-d97a7d00-8f8f-11ea-9326-ad7da0ad6233.gif)
This application acts in 2 parts: 

1. It takes resource identifiers from ArchivesSpace as inputs, searches
the ArchivesSpace database, exports EAD.xml records for the resources
specified, cleans the EAD.xml files, and saves them locally.
2. Upon Upload, EAD.xml files as selected by the user are uploaded to the 
XTF finding aid website/database and the program indexes just those records
uploaded/changed.

## Requirements
1. requirements.txt - this file contains all the dependencies needed to run
the program.
2. A computer with a processor that has at least 2 cores and 2 threads.

## Process
This is a walkthrough of the program and how it functions.
### Login Windows
Upon running the program, the user is met with 2 windows:
1. ArchivesSpace login credentials - input your username, password, and the ArchivesSpace
API URL (if not specified in secrets.py)
2. XTF login credentials - input your username, password, the XTF Hostname and XTF Remote
Path (if not specified in secrets.py)
### Main Screen
This screen displays a multiline text input (Large Box # 1) on the left 
used for inputting resource identifiers. On the right is an output terminal (Large Box # 2), 
which displays messages from the program for the user.

There are 3 buttons on the bottom:
1. Search and Clean - When a user inputs a resource identifier in the multiline text import 
(Large Box #1), this button will search the ArchivesSpace database for resource identifiers
that match the inputs. It will then take those it found and run them through a cleanup script
called cleanup.py and save them to a local folder called clean_eads.

    1. Open Raw ASpace exports (Optional Parameter) - Checking this will save the EAD.xml
    files as exported by ArchivesSpace and open a file explorer window in a folder called
    source_eads. These EAD.xml files are NOT run through cleanup.py script.
2. Open Output - This button opens a file explorer window of the clean_eads folder. This is 
where all exported EAD.xml files are stored after they are run through cleanup.py.
3. Upload - This generates a window allowing a user to select one ore more files stored in 
clean_eads (EAD.xml files after run through cleanup.py).
### Upload Window
This screen displays a window with a listbox with all the files stored in the folder 
clean_eads. Users can select what files they want and click the Upload to XTF button. This 
button does 2 things:
1. It uploads the files to the xtf_remote_path as specified in secrets.py or whatever else
was specified by the user upon logging in.
2. It re-indexes only the records that were uploaded/changed by the user.
## Settings
TO BE FILLED IN LATER
## Testing
Right now, the best way to test the program is to input resource identifiers and try uploading
them to XTF. Some examples of Hargrett and Russell resource identifiers include:

* ms697
* ms905 - biggest one, will take a long time to export and index
* ms2929
* RBRL/044/CFH
* RBRL/112/JRR
* RBRL/109/JHH
* RBRL/067/HEM

If you want to generate errors, input any string or random numbers, such as "hello world"
or 42
## Code Structure
### as_xtf_GUI.py
This file acts as the Graphics User Interface (GUI) for the program. It uses 
PySimpleGUI and its dependencies. There are _5_ functions in the program.
#### run_gui()
There's a lot to this function, so get ready for a wild and long ride.... This function 
handles the GUI operation as outlined by PySimpleGUI's guidelines. There are 2 components
to it, the setup code and the _while_ loop.
##### Setup Code
`sg.ChangeLookAndFeel()` changes the theme of the GUI (colors, button styles, etc.).
`cleanup_default` and `cleanup_options` store the options if a user wants to specify what 
cleanup operations to run through cleanup.py.
`as_username`, `as_password`, `xtf_username`, `xtf_password`, `xtf_hostname`, and 
`xtf_remote_path` set the values for their appropriate credentials.
`menu_def` sets the options for the toolbar menu.
`simple_col1` and `simple_col2` these are columns that help organize. Any variable with _col
in it is a column for the layout of the GUI. The buttons and objects have keys associated
with them. These are used to help read them as "events" in our while loop below.
`layout_simple` sets the layout for the GUI.
`window_simple` sets the window for the main screen. Any variable with _window follows the
same logic.
##### while loop
The way the loop works is that the program "reads" the Window we made above in the setup code
and returns events and values (`event_simple` and `values_simple`). If a user selects a button
with a specific key as outlined in the layout, that is acted upon under the following
`if` statements.

There are _12_ `if` statements in the while loop:
1. `if event_simple == 'Cancel' or event_simple is None:` - This exits the program for the
user.
2. `if event_simple == "_SEARCH_CLEAN_":` - This activates searching ASpace, exporting, and 
cleaning the EAD.xml files. Under this are `if values_simple["_OPEN_RAW_"] is True:`, which
checks if the user selected the "Open raw ASpace exports" checkbox.
3. `if event_simple == "_OPEN_CLEAN_B_" or event_simple == 'Open Cleaned EAD Folder':` - 
Opens clean_eads folder. Outlined in the toolbar menu
4. `if event_simple == "Open Raw ASpace Exports":` - Opens the source_eads folder. Outlined
in the toolbar menu
5. `if event_simple == "Change ASpace Login Credentials":` - runs the function 
`get_aspace_log()` to set ArchivesSpace login credentials. Outlined in the toolbar menu 
(Edit or File/Settings)
6. `if event_simple == 'Change XTF Login Credentials':` - runs the function `get_xtf_log()`
to set XTF login credentials. Outlined in the toolbar menu (Edit or File/Settings)
7. `if event_simple == "About":` - displays a popup (really another window) describing info
about the program version. Users can select the Check Github button, which will open a 
browser tab to the Github version page for the program. Outlined in the toolbar menu (Help)
8. `if event_simple == "Clear Cleaned EAD Folder":` - deletes all files in clean_eads. 
Outlined in the toolbar menu (File)
9. `if event_simple == "Clear Raw ASpace Export Folder":` - deletes all files in 
source_eads. Outlined in the toolbar menu (File)
10. `if event_simple == "Change Cleanup Defaults":` - activates a popup (window) where users
can change the operations of cleanup.py script. Still working on this (should set all to
true and let users uncheck options??). Outlined in the toolbar menu (Edit or File/Settings)
11. `if event_simple == "_UPLOAD_":` - clicking the button Upload, opens the popup 
(window) for users to upload to XTF. Links out to xtf_upload.py to upload and execute 
an indexing of the most recent files to be uploaded
12. `if event_simple == "Exit":` - exits the program
#### get_aspace_log()
This function gets a user's ArchiveSpace credentials. There are 3 components
to it, the setup code, correct_creds while loop, and the window_asplog_active while loop.
##### Setup Code
    as_username = None # ArchivesSpace credentials to to be set later in the function
    as_password = None # ArchivesSpace credentials to to be set later in the function
    as_api = None # Defaults in the secrets.py file, otherwise enter here
    window_asplog_active = True  # To help break from the login verification while loop
    correct_creds = False # To help break out of the login verification while loop
    close_program = False # If a user hits the X button, it passes that on to the 
    # run_gui() function which closes the program entirely.
##### while correct_creds is False
Yes, I know it's weird. I need to change this. This while loop keeps the ArchivesSpace
login window open until a user fills in the correct credentials and sets `correct_creds`
to True.

It sets the columns for the layout, the layout, and the window.
##### while window_asplog_active is True
Again, I know I could leave off the "is True" part. Just trying to be explicit. The way 
the loop works is that the program "reads" the Window we made above in the setup code and 
returns events and values (event_log and values_log). The window takes the inputs 
provided by the user using `as_username = values_log["_ASPACE_UNAME_"]` for instance.

The try, except statement tries to authorize the user using the ArchivesSpace ASnake
client, which is a package for handling API requests to ArchivesSpace. If it fails to 
authenticate, a popup is generated saying the credentials are incorrect. The cycle continues
until the credentials are correct, or the user exits out of the login window.
#### get_xtf_log()
This function gets a user's XTF credentials. There are 3 components to it, the setup code,
correct_creds while loop, and window_xtflog_active while loop.
##### Setup Code
    xtf_username = None # XTF credentials to to be set later in the function
    xtf_password = None # XTF credentials to to be set later in the function
    xtf_host = None # Defaults in the secrets.py file, otherwise enter here
    xtf_remote_path = None # Defaults in the secrets.py file, otherwise enter here
    window_xtflog_active = True # To help break out of the GUI while loop
    correct_creds = False # To help break from the login verification while loop
    close_program = False # If a user hits the X button, it passes that on to the
    # run_gui() function which closes the program entirely.
##### while correct_creds is False
This while loop keeps the ArchivesSpace login window open until a user fills in the correct
 credentials and sets `correct_creds` to True.

It sets the columns for the layout, the layout, and the window.
##### while window_asplog_active is True
The way the loop works is that the program "reads" the Window we made above in the setup 
code and returns events and values (`event_xlog` and `values_xlog`). The window takes the 
inputs provided by the user using `xtf_username = values_xlog["_XTF_UNAME_"]` for instance.

The try, except statement tries to authorize the user by checking the class variable 
`self.scp` in xtf_upload.py. This is only set if the connection to XTF is successful, found
in the function `connect_remote(self)` in xtf_upload.py. If it fails to authenticate, 
a popup is generated saying the credentials are incorrect. The cycle continues
until the credentials are correct, or the user exits out of the login window.
#### as_export_wrapper()
My attempt at threading the ArchivesSpace export
#### xtf_upload_wrapper()
My attempt at threading the XTF upload and re-indexing
### as_export.py
This script searches the ArchivesSpace database for a user-input resource identifier and 
exports an EAD.xml file of the resource if found. There are 2 functions in the script.

The script executes a try, except clause searching for the existance of a folder called
source_eads. If it does not find the folder, it will generate it at the same level as
the script.
#### fetch_results()
##### Required Parameters:
1. input_id - accepts 1 resource identifier at a time (str)
2. as_username - (str)
3. as_password - (str)
4. as_api - (str)

This function takes a resource indentifier as input by the user in the GUI and searches 
ArchivesSpace for a resource that matches the identifier. If it matches with a resource,
it then extracts the resource URI and the resource repository number and returns them. If
an error occurs in any step of the process, a tuple is returned with None as the first
return and a string detailing the error.

The steps for the this function are as follows:
1. Assign `resource_uri` and `resource_repo` to empty strings.
2. Try, Except to initiate an ASnake client. ArchivesSnake is a package to help work with
the ArchivesSpace API. Assign the client as variable `client`.
3. If the input contains either a - or . in it, split the id and add each part to the list
 `id_lines`.
 4. Perform a search using client.get (similar to request.get).
    1. In the ArchivesSpace API, we use the endpoint /search to search across the entire 
    instance. https://archivesspace.github.io/archivesspace/api/#search-this-archive
    2. Parameters:
        1. `"q": 'four_part_id:' + input_id` - q is the optional search query (str), we 
        include "four_part_id:" as that narrows our search to looking for the complete
        resource identifier. We add the input_id as a whole.
        2. `"page": 1` - this is the only option so far, it will return 10 results if 
        the user input returns multiple results. I need to change this to `get_paged`
        and account for returning more than 10 results. So far, I haven't returned more
        than 10.
        3. `"type": ['resource']` - this specifies that we are looking for resources only
 5. We check the status code of the value of `search_resources`. If it is not 200, 
 return None and a string with an error message to be output to the terminal.
 6. Take the value of search_resources, load the it as a json string, extract the content
  and decode it.
 7. If there are results, begin counting the results and set matching and non-matching
 results as dictionaries with URI's as keys and the resource title as their values.
 8. `for id_num in total_id_lines:` - the following is a little confusing, but the basic
 summary is we want to matchthe resource identifier with what the user input. If the 
 identifier is more than 1 part, we are checking that the splits we did above on the 
 user input match the number of id parts that exist in the json data for the resource.
 If the above is true, get the URI for the resource, split it on "/"'s and take the 
 last number as the value of `resource_uri` and the 3rd part [2] index as the 
 `resource_repo`
 9. Any results that fail this are put in the `non_match_results` dictionary and None is
 returned along with an error message detailing what resources did show up in the search.
#### export_ead()
##### Parameters
1. input_id - accepts 1 resource identifier at a time (str)
2. resource_repo - resource repository number (int)
3. resource_uri - resource URI (int). Really this is the identifier ArchivesSpace uses
4. as_username - (str)
5. as_password - (str)
6. as_api - (str)
7. include_unpublished=False - Optional parameter - need to integrate
8. include_daos=True - Optional parameter - need to integrate
9. numbered_cs=True - Optional parameter - need to integrate
10. print_pdf=False - Optional parameter - need to integrate
11. ead3=False - Optional parameter - need to integrate

This function handles exporting EAD.xml files from ArchivesSpace. The steps for this 
function are as follows:
1. Try, Except to initiate an ASnake client. ArchivesSnake is a package to help work with
the ArchivesSpace API. Assign the client as variable `client`.
2. Run a client.get (similar to request.get) to make a call to the ArchivesSpace API to
export an EAD.xml file of a specific resource record.
    1. In the ArchivesSpace API, we use the endpoint 
    repositories/{}/resource_descriptions/{}.xml? as documented here:
     https://archivesspace.github.io/archivesspace/api/#get-an-ead-representation-of-a-resource
    2. Parameters:
        1. `'include_unpublished': False` - doesn't include unpublished portions of the resource
        2. `'include_daos': True` - include digital objects
        3. `'numbered_cs': True` - include numbered container levels
        4. `'print_pdf': False` - do not export resource as pdf 
        5. `'ead3': False` - do not use EAD3 schema, instead defaults to EAD2002
3. `if request_ead.status_code == 200:` - check if request was successful
    1. `if "/" in input_id:` - some resource identifiers contain backslashes. This messes
    with assigning a filepath, so we swap / with _
4. `with open(filepath, "wb") as local_file:` - write the file's content to the 
source_eads folder and return the filepath and result string (" Done")
### cleanup.py
This script runs a series of xml and string cleanup operations on an EAD.xml file. The
function `cleanup_eads` iterates through all the files in the folder source_eads
and creates a class instance of `EADRecord`, running a host of class methods on the 
EAD.xml file and returns it to the function, which writes the new file to the folder
clean_eads.

The code begins with a for loop checking if the folders source_eads and clean_eads
exist. If either do not exist, they are created there.
#### Class EADRecord
This class hosts 12 different methods, each designed to modify an EAD.xml file according
to guidelines set by the Hargrett and Russell library for display on their XTF finding
aid websites, as well as other measures to match some of Harvard's EAD schematron
checks. This produces an EAD.xml file that is EAD2002 compliant.

The following methods will be described briefly.
1. `add_eadid()` - Takes the resource identifier as listed in ArchivesSpace and
copies it to the <eadid> element in the EAD.xml file.
2. `delete_empty_notes()` - Searches for every `<p>` element in the EAD.xml file and 
checks if there is content in the element. If not, it is deleted.
3. `edit_extents()` - Does 2 things. It deletes any empty `<extent>` elements and 
removes non-alphanumeric characters from the beginning of extent elements. An example
would be: `<extent>(13.5x2.5")</extent>`. This would change to `<extent>13.5x2.5"</extent>`.
4. `add_certainty_attr()` - Adds the attribute `certainty="approximate"` to all dates
that include words such as circa, ca. approximately, etc.
5. `add_label_attr()` - Adds the attribute `label="Mixed Materials"` to any container
element that does not already have a label attribute.
6. `delete_empty_containers()` - Searches an EAD.xml file for all container elements
and deletes any that are empty.
7. `update_barcode()` - This adds a `physloc` element to an element when a container has
a label attribute. It takes an appended barcode to the label and makes it the value
of the physloc tag.
8. `remote_at_leftovers()` - Finds any unitid element with a type that includes an 
Archivists Toolkit unique identifier. Deletes that element.
9. `count_xlinks()` - Counts every attribute that occurs in a `<dao>` element.
10. `clean_unused_ns()` - Removes any unused namespaces in the EAD.xml file.
11. `clean_do_dec()` - Removes `xlink:` prefixes in all attributes. Replaces other
namespaces not removed by `clean_unused_ns()` in the `<ead>` element with an empty
`<ead>` element.
12. `clean_suite()` - Runs the above methods according to what the user specified
in the custom_clean parameter. Will also add a doctype to the EAD.xml file and encode
it in UTF-8.
#### cleanup_eads()
This function iterates through all the files located in source_eads, uses the lxml
package to parse the file into an lxml element, passes the lxml elemnent through the
EADRecord class, runs the clean suite against the lxml element, then writes it
to a file in our clean_eads folder.
##### Parameters
1. custom_clean (list)- A list of strings as passed from as_xtf_GUI.py that determines
what methods will be run against the lxml element when running the `clean_suite()`
method. The user can specify what they want cleaned in as_xtf_GUI.py, so this
is how those specifications are passed.
2. keep_raw_exports=False - Optional Parameter - if a user in as_xtf_GUI.py specifies
to keep the exports that come from as_export.py, this parameter will prevent the
function from deleting those files in source_eads. NOT SURE is this is how I want it
to be designed.
### xtf_upload.py
This script comes mostly from Todd Birchard's blog post found here:
https://hackersandslackers.com/automate-ssh-scp-python-paramiko/

It allows for a connection to XTF website using the the paramiko package. While the
blog post connects via SSH, this program connects via user login credentials. This 
substitutes SSH key verification in the function `connect_remote()` for username
and password.