const fbadmin = require('firebase-admin')
const _ = require('lodash')
const debug = require('debug')('cl8.firebase.wrapper')

module.exports = FireBaseAuthWrapper

/**
 * A wrapper around the Firebase API, to return basic javascript objects as much
 * as possible and hide all the futzing around with fetching refs, calling toJSON(),
 * and val().
 *
 *
 * @constructor
 * @param {any} serviceAccount a json file as created by firebase, with a private in it
 * @param {any} dbUrl a realtime database url along the lines of
 * 'https://constellate-test.firebaseio.com'
 * @returns
 */
function FireBaseAuthWrapper (serviceAccount, dbUrl) {
  var admin = fbadmin.initializeApp({
    credential: fbadmin.credential.cert(serviceAccount),
    databaseURL: dbUrl
  })
  /**
   * Fetches the first 1000 users in an account.
   * We assume we don't have more than 1000 users, and instead return the user array
   *
   * https://firebase.google.com/docs/reference/admin/node/admin.auth.Auth#listUsers
   * https://firebase.google.com/docs/reference/admin/node/admin.auth.ListUsersResult
   *
   *
   * @returns Array of user objects
   */
  function getUsers () {
    return admin
      .auth()
      .listUsers()
      .then(result => {
        return result.users
      })
      .catch(err => {
        debug(err)
      })
  }

  function deleteUser (user) {
    debug(user)
    // We can't control the ids these use, so we're better off:
    // fetching by email, then
    // fetch the id
    return admin
      .auth()
      .getUserByEmail(user.fields.email)
      .then(returnedUser => {
        if (typeof returnedUser !== 'undefined') {
          // debug(returnedUser.uid)\
          return admin
            .auth()
            .deleteUser(returnedUser.uid)
            .catch(err => {
              debug('auth:error')
              debug(err)
            })
        }
      })
      .catch(function (error) {
        if (error.errorInfo.code == 'auth/user-not-found') {
          debug('user no longer exists:', user.fields.email)
        }
        return user
        // debug(error)
      })
  }

  function checkForUser (user) {
    return admin
      .auth()
      .getUserByEmail(user.fields.email)
      .then(function (userRecord) {
        // See the UserRecord reference doc for the contents of userRecord.
        debug(
          'Successfully fetched user data:',
          userRecord.uid,
          userRecord.email
        )
        return userRecord
      })
  }

  /**
   *
   *
   * @param {any} user
   * @returns
   */
  function getOrCreateUser (user) {
    return checkForUser(user)
      .then(function (newUser) {
        // debug('found user:', newUser)
        return newUser
      })
      .catch(function (error) {
        if (error.errorInfo.code == 'auth/user-not-found') {
          let u = {
            uid: user.id,
            email: user.fields.email
          }
          return admin
            .auth()
            .createUser(u)
            .then(function (newUser) {
              debug('Successfully created new user:', u.uid, u.email)
              return newUser
            })
            .catch(err => {
              if (err.errorInfo.code == '"auth/uid-already-exists"') {
                return newUser
              }
            })
        }
        if (error.errorInfo.code == 'auth/email-already-exists') {
          debug(error.errorInfo.message, user.email)
          return user
        }
      })
  }

  /**
   * Fetch the current object at 'userlist', as JSON
   *
   * @async
   * @returns Array of objects
   */
  async function getUserList () {
    debug('fetching user list from database')
    const userListRef = await admin
      .database()
      .ref('userlist')
      .once('value')

    if (userListRef.val()) {
      return Object.values(userListRef.val())
    } else {
      return []
    }
  }

  /**
   * Accepts a user object, and list of users, and either attempts to add the user to the list
   * or returns the user matching the id of the user provided, from the list
   *
   * @param {Object} user, with ID
   * @param {Object} userList, containing users, with keyed by ID
   * @returns {object} result, with boolean} saying if this was retreived or a new value, and 'user' key
   */
  async function getOrCreateUserinUserList (user, userList) {
    // check for existence of user
    const matchesUserId = returnedUser => returnedUser.id == user.id
    const filteredUsers = _.filter(userList, matchesUserId)

    if (filteredUsers.length > 0) {
      // we have our user, return early
      debug('getOrCreateUserinUserList: Found our user in the list')
      return { found: true, user: filteredUsers[0] }
    }

    // looks like we have no user, so create one
    debug('Creating our user for this list')
    const createdUser = await createUserInUserList(user)
    return createdUser
  }

  /**
   * Accepts a user object to create and adds it to the userlist on firebase realtime
   *
   *
   * @param {Object} user, with an id,
   * @returns {Object} user
   */
  async function createUserInUserList (user) {
    const userListRef = await admin.database().ref('userlist')

    try {
      const createdUser = await userListRef.push(user)
      const userResult = await createdUser.once('value')
      debug(
        'createUserInUserList: returning newly added user',
        userResult.toJSON().id
      )

      return { found: false, user: userResult.toJSON() }
    } catch (e) {
      debug('error adding user', e)
    }
  }

  /**
   * Adds a user to the user list, and returns the user
   *
   * @param {any} user
   * @param {Array|null} userList
   * @returns {Objject}
   */
  async function addUserToUserList (user, userList) {
    if (typeof userList === 'undefined') {
      throw Error("I couldn't see an userList provided, please provide one")
    }

    debug('addUserToUserList: adding user to firebase database:')

    // adds a user to the userlist data structure in firebase
    const returnedUser = await getOrCreateUserinUserList(user, userList)

    return returnedUser
  }

  // TODO: implement this, when we need it
  // function removeUserfromUserList (user) {}

  function updateUserInUserList (user) {
    return getUserList(admin).then(function (userlist) {
      let usersArray = _.values(userlist.val())
      // debug(usersArray[1])
      let filteredUsers = usersArray.filter(function (returnedUser) {
        return returnedUser.id == user.id
      })
      // return early - we don't want to change this one
      return filteredUsers[0]
    })
  }

  return {
    getUsers: getUsers,
    deleteUser: deleteUser,
    checkForUser: deleteUser,
    getOrCreateUser: getOrCreateUser,
    getUserList: getUserList,
    addUserToUserList: addUserToUserList,
    updateUserInUserList: updateUserInUserList,
    admin: admin
  }
}
