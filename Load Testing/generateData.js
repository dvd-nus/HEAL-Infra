import { faker } from '@faker-js/faker/locale/en_US';

export const registerData = () => ({
  firstName: `${faker.person.firstName()}`,
  lastName: `${faker.person.lastName()}`,

  email: faker.internet.email(),
  password: faker.internet.password({ length: 12 }),

  phone: faker.string.numeric({ length: 8, allowLeadingZeros: false }),
  nric: faker.string.alphanumeric({ length: 10,  casing: 'upper' }),

  gender: faker.person.sexType().charAt(1),
  dateOfBirth: faker.date.past().toLocaleDateString(),

  role: 'PATIENT',
});
