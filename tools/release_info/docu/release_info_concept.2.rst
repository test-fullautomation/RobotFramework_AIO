Release Info Tool Concept - part 2
==================================

Release info rules for **Minor Releases** and **Major Releases**
----------------------------------------------------------------

* Each **Minor Release** info contains the information for exactly this **Minor Release**.
* Each **Major Release** info contains the information for exactly this **Major Release** and additionally the release info of all **Minor Releases** after the previous **Major Release**.

For each **Minor Release**, the version keys in the release files contain exactly two version specifications:
* The version of the current **Minor Release**
* The version of the next higher **Major Release**, which should also contain the information of the current **Minor Release**

For each **Major Release**, the version keys in the release files contain exactly one version specification:
* The version of the current **Major Release**

Each version number consists of **Major Version**, **Minor Version**, and **Patch Version** - and ends with a period. The **Build Number** can be omitted unless it is intended to refer to a specific **Build Number**.

Examples:

* A "0.13.1.x" **Minor Release** requires version key "0.13.1.;0.14.0."
* A "0.13.2.x" **Minor Release** requires version key "0.13.2.;0.14.0."
* A "0.14.0.x" **Major Release** requires version key "0.14.0."

----

*Updated 13.02.2025 / XC-HWP/ESW3-Queckenstedt*

