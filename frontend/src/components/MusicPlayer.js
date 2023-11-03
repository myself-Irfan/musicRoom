import React from "react";
import { Grid, Typography, Card, IconButton, LinearProgress } from "@mui/material";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import PauseIcon from "@mui/icons-material/Pause";
import SkipNextIcon from '@mui/icons-material/SkipNext';

const MusicPlayer = ({ time, duration, image_url, title, artist, is_playing }) => {
    const songProgress = (time/duration) * 100;

    const controlSong = async (is_playing) => {
        const requestOptions = {
            method: "PUT",
            headers: {'Content-Type': 'application/json'},
        };
        try {
            const response = await fetch(`/spotify/${is_playing ? "pause": "play"}`, requestOptions);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }
        } catch (error) {
            console.error(`Fetch failed: ${error}`)
        }
    };

    const skipSong = async () => {
        const requestOptions = {
            method: "POST",
            headers: {'Content-Type': "application/json"}
        };
        fetch('/spotify/skip', requestOptions);
    };

    return (
        <Card>
            <Grid container alignItems="center">
                <Grid item align="center" xs={4}>
                    <img src={image_url} height="100%" width="100%" />
                </Grid>
                <Grid item align="center" xs={8}>
                    <Typography component="h5" variant="h5">{title}</Typography>
                    <Typography color="textSecondary" variant="subtitle1">{artist}</Typography>
                    <div>
                        <IconButton onClick={() => controlSong(is_playing)}>{is_playing ? <PauseIcon /> : <PlayArrowIcon />}</IconButton>
                        <IconButton onClick={() => skipSong()}> <SkipNextIcon /> </IconButton>
                    </div>
                </Grid>
            </Grid>
            <LinearProgress variant="determinate" value={songProgress}/>
        </Card>
    );
};

export default MusicPlayer;