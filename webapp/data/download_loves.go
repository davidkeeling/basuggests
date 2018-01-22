package main

import (
	"bytes"
	"encoding/csv"
	"fmt"
	"io/ioutil"
	"time"
  "os"
  "errors"

	"github.com/peacejam/billionacts/migrations/utils"
	"github.com/peacejam/billionacts/peace"
	"google.golang.org/appengine/datastore"
	"google.golang.org/appengine/log"
)

/*
Go script to fetch "loves" from the Billion Acts datastore.

Used to fetch data for initially training the model, as well as
in the online learning pipeline to fetch new content to retrain.

Relies on the private Billion Acts repository for remote connection
to Google App Engine and the Act of Peace data structure.
*/

const dateFormat = "20060102-1504"

func dateToString(t time.Time) string {
	return t.Format(dateFormat)
}

// For online-learning pipeline
//
// When fetching new content from the database, find content
// newer than the date specified in command line arguments:
var errNoStartDate = errors.New("No latest date specified")

func argsToDate() (time.Time, error) {
	args := os.Args
	if len(args) < 2 {
		return time.Time{}, errNoStartDate
	}
	return time.Parse(dateFormat, args[1])
}

func loveRowHeader() []string {
	return []string{
		"projectID",
		"userID",
		"created",
	}
}

func getLoveRow(love *peace.Love) []string {
	return []string{
		love.ActID,
		love.UserKey.Encode(),
		dateToString(love.Created),
	}
}

func main() {
	c := utils.CreateOAuthContext()
	currentTime := time.Now()
	usingStartDate := false

	query := datastore.NewQuery("Love").Order("-Created")

	startDate, err := argsToDate()
	if err == nil {
		log.Infof(c, "Fetching loves created after %v", startDate)
		query = query.Filter("Created >", startDate)
		usingStartDate = true
	} else if err == errNoStartDate {
		log.Infof(c, "Fetching all loves")
	} else if err != nil {
		log.Criticalf(c, "Error parsing start date: %s", err)
		return
	}

	buf := &bytes.Buffer{}
	writer := csv.NewWriter(buf)

	err = writer.Write(loveRowHeader())
	if err != nil {
		log.Errorf(c, "error writing header to csv: %s", err)
		return
	}

	utils.ReadInBatch(c, query, 100, func(t *datastore.Iterator) error {
		var love peace.Love
		_, iterErr := t.Next(&love)
		if iterErr != nil {
			return iterErr
		}
    if love.UserKey == nil {
      return nil
    }
		return writer.Write(getLoveRow(&love))
	})

	writer.Flush()

	body, err := ioutil.ReadAll(buf)
	if err != nil {
		log.Errorf(c, "Error reading csv: %v", err)
		return
	}

	var filename string
	if usingStartDate {
		filename = fmt.Sprintf("dl_loves(%s).csv", currentTime.Format(dateFormat))
	} else {
		filename = "dl_loves.csv"
	}

	_ = ioutil.WriteFile(filename, body, 0777)
}
