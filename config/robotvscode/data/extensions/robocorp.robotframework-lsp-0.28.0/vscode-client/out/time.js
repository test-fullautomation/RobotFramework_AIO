"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Timing = exports.timeInMillis = exports.sleep = void 0;
exports.sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
function timeInMillis() {
    return new Date().getTime();
}
exports.timeInMillis = timeInMillis;
class Timing {
    constructor() {
        this.initialTime = timeInMillis();
        this.currentTime = this.initialTime;
    }
    elapsedFromLastMeasurement(timeToCheck) {
        let curr = timeInMillis();
        if (curr - this.currentTime > timeToCheck) {
            this.currentTime = curr;
            return true;
        }
        return false;
    }
    getTotalElapsedAsStr() {
        return ((timeInMillis() - this.initialTime) / 1000).toFixed(1) + "s";
    }
}
exports.Timing = Timing;
//# sourceMappingURL=time.js.map