var fs = require('fs');

var package = JSON.parse(fs.readFileSync('package.json'));
var COMMAND_COUNT = 24;
package.contributes.commands = [];
package.contributes.configuration.properties = {};
for (var i = 1; i <= COMMAND_COUNT; i++) {
    var command = `${package.name}.externalCommand${i}`;
    package.contributes.commands.push({
        "command": command,
        "title": `External Command ${i}`
    });
    package.contributes.configuration.properties[`${command}.command`] = {
        "type": "string",
        "default": "",
        "description": "Command"
    };
    package.contributes.configuration.properties[`${command}.args`] = {
        "type": "array",
        "default": [],
        "description": "Arguments"
    };
    package.contributes.configuration.properties[`${command}.cwd`] = {
        "type": "string",
        "default": "",
        "description": "Initial directory"
    };
}
fs.writeFileSync('package.json', JSON.stringify(package, null, 4));