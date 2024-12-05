Adding new components to the RobotFramework AIO
===============================================

The **RobotFramework AIO** is a bundle of separate components. The core component is the Robot Framework. Other components extend the
functionality of this Robot Framework. Each component is developed and under version control within a separate GitHub repository.

To add a new component to the **RobotFramework AIO** project on GitHub, follow these steps:

**Clone some repositories**

The actions described in this document require adjustments in additional repositories, which must be cloned beforehand:

  * `https://github.com/test-fullautomation/RobotFramework_AIO <https://github.com/test-fullautomation/RobotFramework_AIO>`_
  * `https://github.com/test-fullautomation/robotframework-documentation <https://github.com/test-fullautomation/robotframework-documentation>`_

----

**Create a new repository for the component that shall be a part of the RobotFramework AIO**

  Contact Thomas Pollerspoeck (Thomas.Pollerspoeck@de.bosch.com) to create a new repository. 

  Make sure to have the following information available:

  * Name of the repository

    - The name usually starts with ``robotframework-`` for Robot Framework related components.
    - The name usually starts with ``python-`` for Python related components (without immediate reference to the Robot Framework).

  * Name of the component

  * Whether the new component is implemented against the latest Robot Framework (without any extensions; this is called '*original*')
    or is implemented against an older Robot Framework (that contain certain extensions implemented by **RobotFramework AIO** team; this is called '*extended*').

  All repositories containing components for the Robot Framework, follow common design rules and contain a common tool chain and infrastructure. The most relevant
  topics are explained in more detail in the following items. Independent from this, feel free to look at the other repositories to learn more about the internal structure.

  Make sure that you setup your repository in the same way!

----

**Configure the repository**

  The main parameters of a repository are defined within a repository configuration file in JSON format:

  ``<repository>\config\repository_config.json``

  This includes e.g., the name of the repository, the component, the author and so on. The content is used during the setup process and is also taken over in the documentation.

----

**Configure the component documentation**

  A component of the **RobotFramework AIO** can be documented in PDF format. The tool chain that is responsible for generating this PDF file, is part of the repository
  (and also part of the setup dependencies). How this tool chain works is described in more detail within:

  `https://github.com/test-fullautomation/python-genpackagedoc/blob/develop/GenPackageDoc/GenPackageDoc.pdf <https://github.com/test-fullautomation/python-genpackagedoc/blob/develop/GenPackageDoc/GenPackageDoc.pdf>`_
  
  Short form:

  1. Write the common part of the documentation either in RST format or in LaTeX format. The interface description of the new component will be added to the PDF file
     automatically out of the docstrings within the Python code of the component. This requires that the docstrings are written in RST.
  2. Configure the documentation tool chain in the following configuration file within your new repository:

     ``<repository>/packagedoc/packagedoc_config.json``.

     As an example, this is the documentation configuration of the documentation tool chain itself (uses it's functionality for own purposes also):

     `https://github.com/test-fullautomation/python-genpackagedoc/blob/develop/packagedoc/packagedoc_config.json <https://github.com/test-fullautomation/python-genpackagedoc/blob/develop/packagedoc/packagedoc_config.json>`_

----

**Configure the RobotFramework AIO main documentation**

  The **RobotFramework AIO** is documented in the following PDF files:

  * `https://github.com/test-fullautomation/robotframework-documentation/blob/develop/RobotFrameworkAIO/RobotFrameworkAIO_Reference_original.pdf <https://github.com/test-fullautomation/robotframework-documentation/blob/develop/RobotFrameworkAIO/RobotFrameworkAIO_Reference_original.pdf>`_
  * `https://github.com/test-fullautomation/robotframework-documentation/blob/develop/RobotFrameworkAIO/RobotFrameworkAIO_Reference_extended.pdf <https://github.com/test-fullautomation/robotframework-documentation/blob/develop/RobotFrameworkAIO/RobotFrameworkAIO_Reference_extended.pdf>`_

  The documentation of the component within the new repository can be added to the **RobotFramework AIO** main documentation. This needs to be done in the following two files
  (section "IMPORTS"):

  * `https://github.com/test-fullautomation/robotframework-documentation/blob/develop/maindoc/maindoc_configs/maindoc_config_OSS_original.json <https://github.com/test-fullautomation/robotframework-documentation/blob/develop/maindoc/maindoc_configs/maindoc_config_OSS_original.json>`_
  * `https://github.com/test-fullautomation/robotframework-documentation/blob/develop/maindoc/maindoc_configs/maindoc_config_OSS_extended.json <https://github.com/test-fullautomation/robotframework-documentation/blob/develop/maindoc/maindoc_configs/maindoc_config_OSS_extended.json>`_

----

**Update the release info**

  1. Release information regarding the component are defined here:

     ``<component folder within repository>/config/robotframework_aio/release_items_<component name>.json``

     This is not a history of the component! This file contains information that is relevant in the scope of a release of the **RobotFramework AIO**. Therefore, the content
     is adapted to the release frequency of the **RobotFramework AIO** (and not to the release frequency of the component in the new repository).

  2. The **RobotFramework AIO** has its own release items files:

     * `https://github.com/test-fullautomation/RobotFramework_AIO/blob/develop/config/robotframework_aio/release_items_Robotframework_AIO_original.json <https://github.com/test-fullautomation/RobotFramework_AIO/blob/develop/config/robotframework_aio/release_items_Robotframework_AIO_original.json>`_
     * `https://github.com/test-fullautomation/RobotFramework_AIO/blob/develop/config/robotframework_aio/release_items_Robotframework_AIO_extended.json <https://github.com/test-fullautomation/RobotFramework_AIO/blob/develop/config/robotframework_aio/release_items_Robotframework_AIO_extended.json>`_

     These files describe changes and new features in the **RobotFramework AIO** itself. If something needs to be mentioned w.r.t. the component in your new repository, you
     have to add it there.

     Hint: Parts of the release information are taken out of a configuration file that is part of the installed bundle:

     `RobotFramework\python39\Lib\site-packages\RobotFramework_TestsuitesManagement\Config\package_context.json <RobotFramework\python39\Lib\site-packages\RobotFramework_TestsuitesManagement\Config\package_context.json>`_

     The idea behind this is: The release mail shall contain information about what is installed currently. The user is responsible for selecting a proper configuration file
     that fits to the installation!

     *TODO: Add more details about executing the release tool*

----

**Extend the RobotFramework AIO build**

  Add the name of the new repository to the following two configuration files:

  * `https://github.com/test-fullautomation/RobotFramework_AIO/blob/develop/config/repositories/repositories_original.conf <https://github.com/test-fullautomation/RobotFramework_AIO/blob/develop/config/repositories/repositories_original.conf>`_
  * `https://github.com/test-fullautomation/RobotFramework_AIO/blob/develop/config/repositories/repositories_extended.conf <https://github.com/test-fullautomation/RobotFramework_AIO/blob/develop/config/repositories/repositories_extended.conf>`_

  This will make the new repository a part of the **RobotFramework AIO** build.

----

**Tag releases**

  Add the name of the new repository to the following configuration file:

  `https://github.com/test-fullautomation/RobotFramework_AIO/blob/develop/config/repositories/tag_repos.json <https://github.com/test-fullautomation/RobotFramework_AIO/blob/develop/config/repositories/tag_repos.json>`_.

  Every repository listed within this file, will be tagged with the same tag name for each release of the **RobotFramework AIO**.

----

**Publish on PyPi**

  If the component needs to be published on PyPi, update the file:

  `https://github.com/test-fullautomation/RobotFramework_AIO/blob/develop/config/repositories/publish_pypi_repos.txt <https://github.com/test-fullautomation/RobotFramework_AIO/blob/develop/config/repositories/publish_pypi_repos.txt>`_

----

Last update: 03.12.2024
