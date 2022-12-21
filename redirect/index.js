/**
 * Responds to any HTTP request.
 *
 * @param {!express:Request} req HTTP request context.
 * @param {!express:Response} res HTTP response context.
 */

const {Storage} = require('@google-cloud/storage');
const url = require('url');

const bucketName = "project-gcp-weather-krakow";
const storage = new Storage();
const bucket = storage.bucket(bucketName);



exports.weatherInfo = (req, res) => {
    const queryObject = url.parse(req.url, true).query;
    if (Object.keys(queryObject).length !== 2) {
      res.status(404).send("Please pass next query parameters: date=%d.%m.%Y and time=%H:%M")
    }
    const date = queryObject['date'];
    const time = queryObject['time'];

    const splitedDate = date.split(".");
    const splitedTime = time.split(":");

    if (splitedDate.length !== 3 || splitedTime.length !== 2) {
      res.status(404).send("Please pass next query parameters: date=%d.%m.%Y and time=%H:%M")
    }

    const remoteFilePath = `${splitedDate[0]}.${splitedDate[1]}.${splitedDate[2]}/${splitedDate[0]}_${splitedDate[1]}_${splitedDate[2]}_${splitedTime[0]}:${splitedTime[1]}.html`;
    const remoteFile = bucket.file(remoteFilePath);
    return remoteFile.exists().then(function(data) {
      if (data[0] === true) {
        res.redirect(encodeURI(`https://storage.cloud.google.com/${bucketName}/${remoteFilePath}?authuser=1`));
      } else {
        return res.status(404).send("Unfortunately, we do not have weather data for this time");
      }
    });
};
