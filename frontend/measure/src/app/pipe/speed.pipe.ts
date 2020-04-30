import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'speed',
})
export class SpeedPipe implements PipeTransform {
  transform(value: number): string {
    if (value === null) {
      return '';
    }
    if (value === 3) {
      return 'Low Speed, High Resolution';
    } else if (value === 5) {
      return 'Medium Speed, Medium Resolution';
    } else if (value === 10) {
      return 'High Speed, Low Resolution';
    }
    return String(value);
  }
}
