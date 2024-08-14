package db

import (
	"database/sql"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	_ "github.com/lib/pq"
)

const (
	host     = "127.0.0.1"
	port     = 5432
	user     = "postgres"
	password = "test"
	dbname   = "arbie_v3.1"
)

var GLOBAL_DB_OBJ *sql.DB

type Price struct {
	Platform_name   string    `json:"Platform"`
	Record_time     time.Time `json:"Record_time"`
	Price           float32   `json:"Price"`
	Platform_colour string    `json:"Platform_colour"`
}

type Entrant struct {
	Entrant_name string  `json:"Entrant_name"`
	Entrant_id   int     `json:"Entrant_id"`
	Is_scratched int     `json:"Is_scratched"`
	Prices       []Price `json:"Prices"`
}

type Complete_Race struct {
	Track_name string    `json:"Track_name"`
	Round      int       `json:"Round"`
	Start_time time.Time `json:"Start_time"`
	Race_id    int       `json:"Race_id"`
	Entrants   []Entrant `json:"Entrants"`
}

type Price_Instance struct {
	Odds        float32   `json:"Odds"`
	Record_time time.Time `json:"Record_time"`
}

type Platform_Entrant_Series struct {
	Platform_name   string           `json:"Platform_name"`
	Platform_colour string           `json:"Platform_colour"`
	Prices          []Price_Instance `json:"Prices"`
}

type Entrant_Platform_Price_History struct {
	Platform_name string `json:"Platform_name"`
}

type Race struct {
	Track_name string    `json:"Track_name"`
	Round      int       `json:"Round"`
	Start_time time.Time `json:"Start_time"`
	Race_id    int       `json:"Race_id"`
}

type On_day_meet struct {
	Track_name string `json:"Track_name"`
	Races      []Race `json:"Races"`
}

func init() {
	open_connection()
}

func open_connection() {
	psqlInfo := fmt.Sprintf("host=%s port=%d user=%s "+
		"password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	db, err := sql.Open("postgres", psqlInfo)
	if err != nil {
		fmt.Println(err)
	}

	GLOBAL_DB_OBJ = db
}

func exec_query(query string, c *gin.Context) *sql.Rows {
	rows, err := GLOBAL_DB_OBJ.Query(query)
	if err != nil {
		return nil
	}
	return rows
}

func Get_Next_2_Go_Races(c *gin.Context) {
	rows := exec_query("SELECT track_name, round, start_time, race.race_id FROM race JOIN track ON race.track_id = track.track_id WHERE start_time > NOW() ORDER BY start_time ASC;", c)

	all_races := make([]Race, 0)
	for rows.Next() {
		var cur_race Race
		if err := rows.Scan(&cur_race.Track_name, &cur_race.Round, &cur_race.Start_time, &cur_race.Race_id); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to scan row"})
			rows.Close()
			return
		}
		all_races = append(all_races, cur_race)
	}
	if err := rows.Err(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Error occurred during row iteration"})
		rows.Close()
	}

	rows.Close()
	c.IndentedJSON(http.StatusOK, all_races)
}

func Get_Day_Races(c *gin.Context, date int) {
	timestamp := int64(date)
	seconds := timestamp / 1000
	dateTime := time.Unix(seconds, 0)
	isoFormat := dateTime.Format(time.RFC3339)

	rows := exec_query("SELECT DISTINCT track_name FROM race JOIN track ON race.track_id = track.track_id WHERE DATE(start_time) = DATE('"+isoFormat+"');", c)
	races := make([]On_day_meet, 0)
	if rows != nil {
		for rows.Next() {
			var single_race_name On_day_meet
			if err := rows.Scan(&single_race_name.Track_name); err != nil {
				rows.Close()
				return
			}

			meet_race := make([]Race, 0)
			meet_race_rows := exec_query("SELECT track_name,round,start_time,race.race_id FROM race JOIN track ON race.track_id = track.track_id WHERE DATE(start_time) = DATE('"+isoFormat+"') AND track_name = '"+single_race_name.Track_name+"' ORDER BY round ASC;", c)
			for meet_race_rows.Next() {
				var cur_race Race
				if err := meet_race_rows.Scan(&cur_race.Track_name, &cur_race.Round, &cur_race.Start_time, &cur_race.Race_id); err != nil {
					meet_race_rows.Close()
					return
				}
				meet_race = append(meet_race, cur_race)
			}
			meet_race_rows.Close()
			single_race_name.Races = meet_race
			races = append(races, single_race_name)
		}
	}
	rows.Close()

	c.JSON(http.StatusOK, races)
}

func Get_Related_Race_Rounds(c *gin.Context, race_id int) {
	race_id_str := strconv.Itoa(race_id)
	rows := exec_query("SELECT track.track_name,race.round,race.start_time,race.race_id FROM race JOIN track ON race.track_id = track.track_id WHERE DATE(race.start_time) in (SELECT DATE(start_time) FROM race WHERE race_id = "+race_id_str+") AND race.track_id in (SELECT race.track_id FROM race WHERE race_id = "+race_id_str+") ORDER BY race.round;", c)
	races := make([]Race, 0)
	if rows != nil {
		for rows.Next() {
			var cur_race Race
			if err := rows.Scan(&cur_race.Track_name, &cur_race.Round, &cur_race.Start_time, &cur_race.Race_id); err != nil {
				rows.Close()
				return
			}
			races = append(races, cur_race)
		}
		rows.Close()
	}

	c.JSON(http.StatusOK, races)
}

func Get_Race_Details(c *gin.Context, race_id int) []Complete_Race {
	race_id_str := strconv.Itoa(race_id)
	rows := exec_query("SELECT track.track_name, race.round, race.start_time, race.race_id FROM race JOIN track ON race.track_id = track.track_id WHERE race.race_id = "+race_id_str+";", c)

	all_races := make([]Complete_Race, 0)
	for rows.Next() {
		var cur_race Complete_Race
		if err := rows.Scan(&cur_race.Track_name, &cur_race.Round, &cur_race.Start_time, &cur_race.Race_id); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to scan row"})
			return nil
		}
		all_races = append(all_races, cur_race)
	}

	rows.Close()
	if err := rows.Err(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Error occurred during row iteration"})
		return nil
	}

	return all_races
}

func Get_Race_Entrants(c *gin.Context, race_id int) []Entrant {
	race_id_str := strconv.Itoa(race_id)
	rows := exec_query("SELECT entrant.entrant_id, horse.name, entrant.is_scratched FROM race JOIN entrant ON race.race_id = entrant.race_id JOIN horse ON horse.horse_id = entrant.horse_id WHERE race.race_id = "+race_id_str+";", c)

	entrants := make([]Entrant, 0)
	for rows.Next() {
		var entrant Entrant
		if err := rows.Scan(&entrant.Entrant_id, &entrant.Entrant_name, &entrant.Is_scratched); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to scan row"})
			return nil
		}
		entrants = append(entrants, entrant)
	}

	rows.Close()
	if err := rows.Err(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Error occurred during row iteration"})
		return nil
	}

	return entrants
}

func Get_Entrant_Timeseries_Prices(c *gin.Context, entrant_id int) []Platform_Entrant_Series {
	entrant_id_str := strconv.Itoa(entrant_id)
	rows := exec_query("SELECT odds.platform_name, platforms.theme_color FROM odds JOIN platforms ON odds.platform_name = platforms.platform_name WHERE odds.entrant_id = "+entrant_id_str+" GROUP BY odds.platform_name, platforms.theme_color;", c)

	platform_offerings := make([]Platform_Entrant_Series, 0)
	for rows.Next() {
		var cur_platform Platform_Entrant_Series
		if err := rows.Scan(&cur_platform.Platform_name, &cur_platform.Platform_colour); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to scan row"})
			rows.Close()
			return nil
		}
		historic_entrant_platform_offerings := exec_query("SELECT odds, record_time FROM odds WHERE entrant_id="+entrant_id_str+" AND platform_name='"+cur_platform.Platform_name+"' ORDER BY record_time ASC;", c)
		price_instances := make([]Price_Instance, 0)
		for historic_entrant_platform_offerings.Next() {
			var cur_price Price_Instance
			if err := historic_entrant_platform_offerings.Scan(&cur_price.Odds, &cur_price.Record_time); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to scan row"})
				historic_entrant_platform_offerings.Close()
				return nil
			}
			price_instances = append(price_instances, cur_price)
		}
		cur_platform.Prices = price_instances
		platform_offerings = append(platform_offerings, cur_platform)

		historic_entrant_platform_offerings.Close()
	}
	rows.Close()

	if err := rows.Err(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Error occurred during row iteration"})
		return nil
	}

	return platform_offerings
}

func Get_Platform_Offerings(c *gin.Context, entrant_id int) []Price {
	entrant_id_str := strconv.Itoa(entrant_id)
	rows := exec_query("SELECT DISTINCT platform_name FROM odds WHERE entrant_id = "+entrant_id_str+";", c)

	platform_offerings := make([]Price, 0)
	for rows.Next() {
		var platform Price
		if err := rows.Scan(&platform.Platform_name); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to scan row"})
			return nil
		}
		platform = Get_Current_Platform_Price(c, platform.Platform_name, entrant_id)
		platform_offerings = append(platform_offerings, platform)
	}

	rows.Close()
	if err := rows.Err(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Error occurred during row iteration"})
		return nil
	}

	return platform_offerings
}

func Get_Current_Platform_Price(c *gin.Context, platform_name string, entrant_id int) Price {
	entrant_id_str := strconv.Itoa(entrant_id)
	rows := exec_query("SELECT odds.platform_name, odds.odds, odds.record_time, platforms.theme_color FROM odds JOIN platforms ON odds.platform_name = platforms.platform_name WHERE odds.entrant_id = "+entrant_id_str+" AND odds.platform_name = '"+platform_name+"' ORDER BY odds.record_time DESC LIMIT 1;", c)

	var set bool = false
	var platform_price Price
	for rows.Next() {
		if err := rows.Scan(&platform_price.Platform_name, &platform_price.Price, &platform_price.Record_time, &platform_price.Platform_colour); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to scan row"})
		}
		set = true
		break
	}

	rows.Close()
	if !set {
		c.JSON(http.StatusInternalServerError, gin.H{"message": "Failed to scan row"})
	}

	return platform_price
}
