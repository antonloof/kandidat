import { Injectable } from '@angular/core';
import { TitleCasePipe } from '@angular/common';

// prettier-ignore
const ADJECTIVES = ["aggressive","agreeable","ambitious","brave","calm","delightful","eager","faithful","gentle","happy","jolly","kind","lively","nice","obedient","polite","proud","silly","thankful","victorious","witty","wonderful","zealous","angry","bewildered","clumsy","defeated","embarrassed","fierce","grumpy","helpless","itchy","jealous","lazy","mysterious","nervous","obnoxious","panicky","pitiful","repulsive","scary","thoughtless","uptight","worried"];
// prettier-ignore
const NOUNS = ["people", "history", "way", "art", "world", "information", "map", "family", "government", "health", "system", "computer", "meat", "year", "thanks", "music", "person", "reading", "method", "data", "food", "understanding", "theory", "law", "bird", "literature", "problem", "software", "control", "knowledge", "power", "ability", "economics", "love", "internet", "television", "science", "library", "nature", "fact", "product", "idea", "temperature", "investment", "area", "society", "activity", "story"];

@Injectable({
  providedIn: 'root',
})
export class RandomNameService {
  constructor(private titlecase: TitleCasePipe) {}

  get(): string {
    const randAdj = ADJECTIVES[Math.floor(Math.random() * ADJECTIVES.length)];
    const randNoun = NOUNS[Math.floor(Math.random() * NOUNS.length)];
    return this.titlecase.transform(randAdj + ' ' + randNoun);
  }
}
