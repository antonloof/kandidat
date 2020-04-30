import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'speed',
})
export class SpeedPipe implements PipeTransform {
  transform(value: number): string {
    if (value === null) {
      return '';
    }
    if (value === 2) {
      return 'Low Speed, High Resolution';
    } else if (value === 10) {
      return 'Medium Speed, Medium Resolution';
    } else if (value === 20) {
      return 'High Speed, Low Resolution';
    }
  }
}
