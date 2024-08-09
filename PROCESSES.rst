Adding new components
======================

To add a new component to the RobotFramework AIO project on GitHub, follow these steps:

* **Create a new Repository**: Contact Thomas Pollerspoeck (Thomas.Pollerspoeck@de.bosch.com) to create a new repository. 

* **Clone Repository**: Modify the `repositories.conf <https://github.com/test-fullautomation/RobotFramework_AIO/blob/develop/config/repositories/repositories.conf>`_ file to include the new repository. It will clone the repository to integrate to AIO tools.

* **Tag Releases**: For each release package in RobotFramework AIO, it will trigger a tag release for other components. Modify the `tag repos configuration <https://github.com/test-fullautomation/RobotFramework_AIO/blob/develop/config/repositories/tag_repos.json>`_ to ensure a tag is created for the new repository.

* **Publish on PyPi**: If the component needs to be published on PyPi, update the `publish pypi repos <https://github.com/test-fullautomation/RobotFramework_AIO/blob/develop/config/repositories/publish_pypi_repos.txt>`_ file accordingly.

* **Documentation**: Update the `maindoc config OSS <https://github.com/test-fullautomation/robotframework-documentation/blob/develop/maindoc/maindoc_configs/maindoc_config_OSS.json>`_ file in the robotframework-documentation repository to generate all necessary documents related to the new repository.

* **Release Info**: Finally, update the release info at `release items Robotframework AIO <https://github.com/test-fullautomation/RobotFramework_AIO/blob/develop/config/robotframework_aio/release_items_Robotframework_AIO.json>`_ to describe what the new changes in the RobotFramework AIO.
