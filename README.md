> [!WARNING]  
> This is a work in progress and is not ready for production use yet. The API and implementation are subject to changes on minor versions.  
> See the Roadmap for planned features and the [Contributing](#contributing) section for ways to contribute.

<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->

<a name="readme-top"></a>

<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
<div align="center">

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

</div>





<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="https://avatars.githubusercontent.com/u/150265376?s=200&v=4" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">StateForward</h3>

  <p align="center">
    StateForward Python: Simplifying Complexity, One State at a Time.
    <br />
    <a href="https://docs.stateforward.org"><strong>Explore the docs</strong></a>
    <br />
    <br />
    <a href="https://github.com/othneildrew/Best-README-Template">View Demo</a>
    ·
    <a href="https://github.com/othneildrew/Best-README-Template/issues">Report Bug</a>
    ·
    <a href="https://github.com/othneildrew/Best-README-Template/issues">Request Feature</a>
  </p>
</div>



<details open="open">
<summary>Table of Contents</summary>

- [About](#about)
- [Roadmap](#roadmap)
- [Installation](#installation)
- [Getting Started](#getting-started)
  - [Basic Example](#basic-example)
- [Contributing](#contributing)
- [Acknowledgements](#acknowledgements)

</details>

---


## About StateForward Python

[//]: # ([![Product Name Screen Shot][product-screenshot]]&#40;https://example.com&#41;)

StateForward Python is where code complexity meets simplicity. 
This library is your ally in evolving spaghetti code into elegant, robust state machines. 
Say goodbye to the dense forest of if-else statements and welcome a world where adding features doesn’t mean unraveling a complex knot.

With StateForward Python, you’re building on solid ground. 
Your code becomes a clear map of states and transitions, making it easily extendable and a joy to maintain. 
It's about writing software that grows with grace, ensuring that your project's future is as structured and reliable as its present.
<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.


### Installation

#### Pip
1. Install the package
    ```sh
    pip install stateforward
    ```
#### Manually
1. Clone the repo
   ```sh
   git clone https://github.com/stateforward/stateforward_python.git
   ```
2. Initialize virtual environment
    ```bash
    poetry shell 
    ```
3. Install dev dependencies
   ```sh
   poetry install
   ```


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

```python
import stateforward as sf
import asyncio


class OnEvent(sf.Event):
    pass


class OffEvent(sf.Event):
    pass


class LightSwitch(sf.AsyncStateMachine):
    class On(sf.State):
        @sf.decorators.behavior
        async def entry(self, event: OnEvent):
            print("Light on entry")

        @sf.decorators.behavior
        async def exit(self, event: OffEvent):
            print("Light on exit")

    class Off(sf.State):
        @sf.decorators.behavior
        async def entry(self, event: OnEvent):
            print("Light off entry")

        @sf.decorators.behavior
        async def exit(self, event: OffEvent):
            print("Light off exit")

    initial = sf.initial(Off)
    transitions = sf.collection(
        sf.transition(OnEvent, source=Off, target=On),
        sf.transition(OffEvent, source=On, target=Off),
    )


async def main():
    # instantiate a light switch
    light_switch = LightSwitch()
    # start the interpreter and wait for it to be settled
    await light_switch.__interpreter__.start()
    # output the current states of the state machine
    print(light_switch.state)
    # dispatch a OnEvent to the state machine
    await sf.send(OnEvent(), light_switch)
    # output the current states of the state machine
    print(light_switch.state)
    # dispatch a OffEvent to the state machine
    await sf.send(OffEvent(), light_switch)
    print(light_switch.state)


asyncio.run(main())
```
      
_For more examples, please refer to the [Documentation](https://docs.stateforward.org)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Your Name - [@twitter_handle](https://twitter.com/twitter_handle) - email@email_client.com

Project Link: [https://github.com/github_username/repo_name](https://github.com/github_username/repo_name)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* []()
* []()
* []()

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/github_username/repo_name.svg?style=for-the-badge
[contributors-url]: https://github.com/github_username/repo_name/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/github_username/repo_name.svg?style=for-the-badge
[forks-url]: https://github.com/github_username/repo_name/network/members
[stars-shield]: https://img.shields.io/github/stars/github_username/repo_name.svg?style=for-the-badge
[stars-url]: https://github.com/github_username/repo_name/stargazers
[issues-shield]: https://img.shields.io/github/issues/github_username/repo_name.svg?style=for-the-badge
[issues-url]: https://github.com/github_username/repo_name/issues
[license-shield]: https://img.shields.io/github/license/github_username/repo_name.svg?style=for-the-badge
[license-url]: https://github.com/github_username/repo_name/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/linkedin_username
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 