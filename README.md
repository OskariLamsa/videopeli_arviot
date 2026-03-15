# Videopelien arviointi sivusto
## Sovelluksen toiminnot
* Käyttäjä voi luoda tunnuksen ja kirjautua sisään sivustolle.
* Käyttäjä voi etsiä videopelin nimeltä, ja selata arvioita, joita se on saanut.
* Käyttäjä voi kirjoittaa arvion videopelille.
* Käyttäjä voi päivittää kirjoittamiaan arvioita
* Käyttäjä voi lukea tietyn käyttäjän tekemät arviot heidän profiilissaan.
* Käyttäjä voi antaa arviolle peukun ylös, tai alas

 Käyttäjät voivat tehdä suoritusmerkinnän vain olemassa oleville peleille. Eli aloittaessaan arviota, käyttäjä kirjoittaa pelin nimen valitsee sen, jos se löytyy peli-tietokannasta. Arvio on pääasiallinen tietokohde, peukutukset ovat toissijainen tietokohde, ja itse peli-tietokanta on käyttäjälle näkymätön ja staattinen.

## Sovelluksen kuvaus
Nettisivustomme on yksinkertainen abstraktio Metacritic-sivuston tapaisesta videopelien arviointisivusta. Tiedot peleistä elävät erillisessä staattisessa tietokannassa. Yksi entry tietokannassa sisältää pelin nimen, alustan (konsoli, pc), ja julkaisuvuosi. Kun käyttäjä etsii sivustolta videopelin, he näkevät kaikki sille annetut arviot, ja keksiarvon, joka on väliltä 1-5 tähteä. Tämä keskiarvo lasketaan dynaamisesti jokaisen pelihaun yhteydessä. Kun käyttäjä kirjoittaa arvion pelille, he aloittavat etsimällä pelin nimeltä. Se täytyy löytyä staattisesta tietokannasta. Käyttäjä saa kirjoittaa arvion (max 500 merkkiä) ja antaa 1-5 tähteä. Arvio tallennetaan pääasiallisena tietokohteena.
Käyttäjät voivat myös etsiä pelejä alustan perusteella. Kilkkaamalla peliä pääsee kyseisen pelin arvointisivulle
