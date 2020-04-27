import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'mobility',
})
export class MobilityPipe implements PipeTransform {
  transform(value: number): string {
    if (value === null) {
      return '';
    }
    const m2_to_cm2 = 1e4;
    return `${parseFloat((value * m2_to_cm2).toPrecision(4))}`;
  }
}
