
import { mount, shallow, createLocalVue } from '@vue/test-utils'
import Login from '@/components/auth/Login.vue'

import debugLib from 'debug'
const debug = debugLib('cl8.LoginComponent.spec')

// we need to augment our Vue object for this component test
// as we're not evaluating any setup in main.js
const localVue = createLocalVue()

describe('Login.Vue', () => {

  // declare mutable variable
  let wrapper
  let mockStore = {
    getters: {
      isLoading: false,
      signInData: {
        message: null,
        email: null
      }
    },
    dispatch: jest.fn()
  }

  describe('requesting token with valid email', () => {

      beforeEach(() => {
        // set up state as if email was sent
        wrapper = mount(Login, {
          localVue,
          data() {
            return {
              email: 'valid.email@domain.com',
              emailSubmitted: true,
              formIsValid: true
            }
          },
          mocks: {
            $store: {
              getters: {
                isLoading: false,
                signInData: {
                  message: null,
                  email: 'valid.email@domain.com',
                }
              },
              dispatch: mockStore.dispatch
            },
            $t: () => {}
          }
        })
      })

      it('shows new guidance after a user submits their email', async () => {
        expect(wrapper.get('p.next-step-guidance')).toBeTruthy()
      })

      it('sends the provided token to finish sign in', async () => {
        // when we add the token, check that the action is dispatched
        // arguably, triggering this 'from the outside' lives in an
        // e2e test. TODO: work out the idiomatic way to do this
        // with vue
        wrapper.find('[data-name="login-code"]').setValue(123456)
        wrapper.get('[data-name="sign-in"]').trigger('click')

        expect(wrapper.vm.$store.dispatch).toHaveBeenCalledWith('login',
          {email: 'valid.email@domain.com', token: "123456"}
        )
      })
  })
})
