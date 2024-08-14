package db_new

import (
	"arbie/new_models"
	"database/sql"
	"errors"
	"fmt"
	"strconv"

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

func exec_query(query string) *sql.Rows {
	rows, err := GLOBAL_DB_OBJ.Query(query)
	if err != nil {
		return nil
	}
	return rows
}

func Get_Platform_Price_Fluctuations_By_EntrantID(entrant_id int, platform_name string) ([]new_models.Price, error) {
	entrant_id_str := strconv.Itoa(entrant_id)
	rows := exec_query("SELECT odds, record_time FROM odds WHERE entrant_id=" + entrant_id_str + " AND platform_name='" + platform_name + "' ORDER BY record_time DESC;")

	price_fluctuations := make([]new_models.Price, 0)
	for rows.Next() {
		var curr_price_instance new_models.Price
		if err := rows.Scan(&curr_price_instance.Odds, &curr_price_instance.Record_Time); err != nil {
			rows.Close()
			return price_fluctuations, errors.New("scan error")
		}
		price_fluctuations = append(price_fluctuations, curr_price_instance)
	}
	rows.Close()

	return price_fluctuations, nil
}

func Get_Price_By_EntrantID(entrant_id int) ([]new_models.Prices, error) {
	entrant_id_str := strconv.Itoa(entrant_id)
	rows := exec_query("SELECT DISTINCT platform_name FROM odds WHERE entrant_id=" + entrant_id_str + ";")

	all_prices := make([]new_models.Prices, 0)
	for rows.Next() {
		var platform_name string
		if err := rows.Scan(&platform_name); err != nil {
			rows.Close()
			return all_prices, errors.New("scan error")
		}

		platform_prices, err := Get_Platform_Price_Fluctuations_By_EntrantID(entrant_id, platform_name)
		if err != nil {
			rows.Close()
			return all_prices, errors.New("scan error")
		}

		var platform_price new_models.Prices
		if len(platform_prices) > 0 {
			platform_price.Current_Price = platform_prices[0]
		}
		platform_price.Price_Fluctuations = platform_prices
		platform_price.Platform_Name = platform_name

		all_prices = append(all_prices, platform_price)
	}
	rows.Close()

	return all_prices, nil
}

func Get_Entrant_By_ID(entrant_id int) (new_models.Entrant, error) {
	entrant_id_str := strconv.Itoa(entrant_id)
	rows := exec_query("SELECT entrant.entrant_id, horse.name, entrant.is_scratched FROM entrant JOIN horse ON entrant.horse_id=horse.horse_id WHERE entrant.entrant_id=" + entrant_id_str + ";")

	var entrant new_models.Entrant
	for rows.Next() {
		if err := rows.Scan(&entrant.Entrant_Id, &entrant.Entrant_Name, &entrant.Is_Scratched); err != nil {
			return entrant, errors.New("scan error")
		}
		break
	}

	return entrant, nil
}

func Get_EntrantIDs_By_RaceID(race_id int) ([]int, error) {
	race_id_str := strconv.Itoa(race_id)
	rows := exec_query("SELECT entrant_id FROM entrant WHERE race_id=" + race_id_str + ";")

	entrant_ids := make([]int, 0)
	for rows.Next() {
		var entrant_id int
		if err := rows.Scan(&entrant_id); err != nil {
			rows.Close()
			return entrant_ids, errors.New("scan error")
		}
		entrant_ids = append(entrant_ids, entrant_id)
	}

	return entrant_ids, nil
}

func Get_Race_By_ID(race_id int) (new_models.Race, error) {
	race_id_str := strconv.Itoa(race_id)
	rows := exec_query("SELECT track.track_id, race.race_id, start_time, round, track.track_name FROM race JOIN track ON race.track_id=track.track_id WHERE race.race_id=" + race_id_str + ";")

	var curr_race new_models.Race
	for rows.Next() {
		if err := rows.Scan(&curr_race.Track_Id, &curr_race.Race_Id, &curr_race.Start_Time, &curr_race.Round, &curr_race.Track_Name); err != nil {
			rows.Close()
			return curr_race, errors.New("scan error")
		}
		break
	}

	rows.Close()
	return curr_race, nil
}

func Get_Next_2_Go_RaceIds() ([]int, error) {
	rows := exec_query("SELECT race.race_id FROM race WHERE start_time > NOW() AND DATE(start_time)=DATE(NOW()) ORDER BY start_time ASC;")
	race_ids := make([]int, 0)
	for rows.Next() {
		var cur_race_id int
		if err := rows.Scan(&cur_race_id); err != nil {
			rows.Close()
			return race_ids, errors.New("scan error")
		}
		race_ids = append(race_ids, cur_race_id)
	}
	rows.Close()
	return race_ids, nil
}

func Get_Related_RaceIds(race_id int) ([]int, error) {
	race_id_str := strconv.Itoa(race_id)
	rows := exec_query("SELECT race.race_id FROM race JOIN track ON race.track_id = track.track_id WHERE DATE(race.start_time) in (SELECT DATE(start_time) FROM race WHERE race_id = " + race_id_str + ") AND race.track_id in (SELECT race.track_id FROM race WHERE race_id = " + race_id_str + ") ORDER BY race.round;")

	race_ids := make([]int, 0)
	for rows.Next() {
		var cur_race_id int
		if err := rows.Scan(&cur_race_id); err != nil {
			return race_ids, errors.New("scan error")
		}
		race_ids = append(race_ids, cur_race_id)
	}

	return race_ids, nil
}

func Get_RaceIDs_On_Day(date_iso_string string) ([]int, error) {
	rows := exec_query("SELECT DISTINCT race.race_id FROM race WHERE DATE(start_time)=DATE('" + date_iso_string + "');")
	race_ids := make([]int, 0)
	for rows.Next() {
		var current_race_id int
		if err := rows.Scan(&current_race_id); err != nil {
			rows.Close()
			return race_ids, errors.New("scan error")
		}
		race_ids = append(race_ids, current_race_id)
	}
	rows.Close()
	return race_ids, nil
}

func Get_Trackname_By_TrackId(track_id int) (string, error) {
	track_id_str := strconv.Itoa(track_id)
	rows := exec_query("SELECT track.track_name FROM track WHERE track.track_id=" + track_id_str + ";")

	var track_name string
	for rows.Next() {
		if err := rows.Scan(&track_name); err != nil {
			return track_name, errors.New("scan error")

		}
		break
	}
	rows.Close()
	return track_name, nil
}
