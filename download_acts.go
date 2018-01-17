package main

import (
	"bytes"
	"encoding/csv"
	"errors"
	"fmt"
	"io/ioutil"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/peacejam/billionacts/migrations/utils"
	"github.com/peacejam/billionacts/peace"
	"google.golang.org/appengine/datastore"
	"google.golang.org/appengine/log"
)

/*
Go script to fetch acts of peace from the Billion Acts datastore.
Saves results as a CSV to be passed into Python for data cleaning,
NLP processing and topic modeling.

Used to fetch data for initially training the model, as well as
in the online learning pipeline to fetch new content to retrain.

Relies on the private Billion Acts repository for remote connection
to Google App Engine, and the Act of Peace data structure.
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

func argsToDate(args []string) (time.Time, error) {
	if len(args) < 2 {
		return time.Time{}, errNoStartDate
	}
	return time.Parse(dateFormat, args[1])
}

func projectRowHeader() []string {
	return []string{
		"title",
		"issues",
		"context",
		"plan",
		"accomplishments",
		"description",
		"call_to_action",
		"focusareas",
		"created",
		"projectid",
	}
}

func getProjectRow(proj *peace.Project) []string {
	focusareaStrings := []string{}
	for _, fa := range proj.AreaID {
		focusareaStrings = append(focusareaStrings, strconv.Itoa(int(fa)))
	}
	return []string{
		proj.Name,
		proj.Issues,
		proj.Context,
		proj.Plan,
		proj.Accomplishments,
		proj.Description,
		proj.CtaDescription,
		strings.Join(focusareaStrings, " "),
		dateToString(proj.Created),
		proj.ProjectID,
	}
}

func main() {
	c := utils.CreateOAuthContext()
	currentTime := time.Now()
	usingStartDate := false

	query := datastore.NewQuery("Project").Order("-Created")

	startDate, err := argsToDate(os.Args)
	if err == nil {
		log.Infof(c, "Fetching acts created after %v", startDate)
		query = query.Filter("Created >", startDate)
		usingStartDate = true
	} else if err == errNoStartDate {
		log.Infof(c, "Fetching all acts")
	} else if err != nil {
		log.Criticalf(c, "Error parsing start date: %s", err)
		return
	}

	buf := &bytes.Buffer{}
	writer := csv.NewWriter(buf)

	err = writer.Write(projectRowHeader())
	if err != nil {
		log.Errorf(c, "error writing header to csv: %s", err)
		return
	}

	utils.ReadInBatch(c, query, 100, func(t *datastore.Iterator) error {
		var proj peace.Project
		key, iterErr := t.Next(&proj)
		if iterErr != nil {
			return iterErr
		}
		proj.ProjectID = key.Encode()
		return writer.Write(getProjectRow(&proj))
	})

	writer.Flush()

	body, err := ioutil.ReadAll(buf)
	if err != nil {
		log.Errorf(c, "Error reading csv: %v", err)
		return
	}

	var filename string
	if usingStartDate {
		filename = fmt.Sprintf("dl_acts(%s).csv", currentTime.Format(dateFormat))
	} else {
		filename = "dl_acts.csv"
	}

	_ = ioutil.WriteFile(filename, body, 0777)
}
