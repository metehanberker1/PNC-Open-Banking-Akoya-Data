import devfulcrum


def main():
    client = devfulcrum.AkoyaClient('024e4a....', 'nPKt....')
    client.update_tokens_auto()  # update tokens automatically (except refresh token)


if __name__ == '__main__':
    main()  # call the user code above
